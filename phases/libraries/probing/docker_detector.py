"""Docker environment discovery and analysis."""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


logger = logging.getLogger(__name__)


class DockerDiscovery:
    """Discovers Docker environment and existing containers for OpenProject."""
    
    def __init__(self):
        """Initialize Docker discovery."""
        self.docker_available = False
        self.docker_client = None
        self._initialize_docker_client()
    
    def _initialize_docker_client(self):
        """Initialize Docker client if available."""
        try:
            import docker
            self.docker_client = docker.from_env()
            # Test connection
            self.docker_client.ping()
            self.docker_available = True
            logger.info("Docker client initialized successfully")
        except ImportError:
            logger.warning("Docker package not available")
        except Exception as e:
            logger.warning(f"Docker not available or not accessible: {e}")
    
    def discover(self) -> Dict[str, Any]:
        """
        Discover Docker environment and existing containers.
        
        Returns:
            Dictionary containing discovered Docker data
        """
        logger.info("Starting Docker discovery")
        
        docker_data = {
            'docker_available': self.docker_available,
            'docker_info': {},
            'containers': [],
            'images': [],
            'networks': [],
            'volumes': [],
            'compose_projects': [],
            'openproject_containers': [],
            'database_containers': [],
            'recommendations': {}
        }
        
        if not self.docker_available:
            logger.warning("Docker not available, skipping Docker discovery")
            docker_data['recommendations']['docker_install'] = (
                "Docker not detected. Please install Docker to run OpenProject."
            )
            return docker_data
        
        try:
            # Get Docker system info
            docker_data['docker_info'] = self._get_docker_info()
            
            # Discover containers
            docker_data['containers'] = self._discover_containers()
            
            # Discover images
            docker_data['images'] = self._discover_images()
            
            # Discover networks
            docker_data['networks'] = self._discover_networks()
            
            # Discover volumes
            docker_data['volumes'] = self._discover_volumes()
            
            # Identify OpenProject-related containers
            docker_data['openproject_containers'] = self._find_openproject_containers(
                docker_data['containers']
            )
            
            # Identify database containers
            docker_data['database_containers'] = self._find_database_containers(
                docker_data['containers']
            )
            
            # Discover Compose projects
            docker_data['compose_projects'] = self._discover_compose_projects()
            
            # Generate recommendations
            docker_data['recommendations'] = self._generate_recommendations(docker_data)
            
            logger.info("Docker discovery completed successfully")
            
        except Exception as e:
            logger.error(f"Docker discovery failed: {e}")
            docker_data['error'] = str(e)
        
        return docker_data
    
    def _get_docker_info(self) -> Dict[str, Any]:
        """Get Docker system information."""
        if not self.docker_client:
            return {}
        
        try:
            info = self.docker_client.info()
            version = self.docker_client.version()
            
            return {
                'version': version.get('Version', 'unknown'),
                'api_version': version.get('ApiVersion', 'unknown'),
                'git_commit': version.get('GitCommit', 'unknown'),
                'build_time': version.get('BuildTime', 'unknown'),
                'containers': info.get('Containers', 0),
                'containers_running': info.get('ContainersRunning', 0),
                'containers_paused': info.get('ContainersPaused', 0),
                'containers_stopped': info.get('ContainersStopped', 0),
                'images': info.get('Images', 0),
                'server_version': info.get('ServerVersion', 'unknown'),
                'storage_driver': info.get('Driver', 'unknown'),
                'memory': info.get('MemTotal', 0),
                'cpus': info.get('NCPU', 0),
                'architecture': info.get('Architecture', 'unknown'),
                'os': info.get('OperatingSystem', 'unknown'),
                'os_version': info.get('OSVersion', 'unknown'),
                'kernel_version': info.get('KernelVersion', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to get Docker info: {e}")
            return {'error': str(e)}
    
    def _discover_containers(self) -> List[Dict[str, Any]]:
        """Discover all Docker containers."""
        if not self.docker_client:
            return []
        
        containers = []
        
        try:
            # Get all containers (running and stopped)
            for container in self.docker_client.containers.list(all=True):
                container_info = {
                    'id': container.id[:12],
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else container.image.id[:12],
                    'status': container.status,
                    'created': container.attrs.get('Created', ''),
                    'ports': self._extract_container_ports(container),
                    'networks': list(container.attrs.get('NetworkSettings', {}).get('Networks', {}).keys()),
                    'volumes': self._extract_container_volumes(container),
                    'environment': self._extract_container_env(container),
                    'labels': container.labels,
                    'command': container.attrs.get('Config', {}).get('Cmd', []),
                    'working_dir': container.attrs.get('Config', {}).get('WorkingDir', ''),
                    'user': container.attrs.get('Config', {}).get('User', ''),
                    'restart_policy': container.attrs.get('HostConfig', {}).get('RestartPolicy', {})
                }
                containers.append(container_info)
        
        except Exception as e:
            logger.error(f"Failed to discover containers: {e}")
        
        return containers
    
    def _extract_container_ports(self, container) -> Dict[str, Any]:
        """Extract port mappings from container."""
        ports = {}
        
        try:
            port_bindings = container.attrs.get('NetworkSettings', {}).get('Ports', {})
            for container_port, host_bindings in port_bindings.items():
                if host_bindings:
                    for binding in host_bindings:
                        host_ip = binding.get('HostIp', '0.0.0.0')
                        host_port = binding.get('HostPort', '')
                        ports[container_port] = f"{host_ip}:{host_port}"
                else:
                    ports[container_port] = "not mapped"
        except Exception as e:
            logger.warning(f"Failed to extract ports for container {container.name}: {e}")
        
        return ports
    
    def _extract_container_volumes(self, container) -> List[Dict[str, str]]:
        """Extract volume mounts from container."""
        volumes = []
        
        try:
            mounts = container.attrs.get('Mounts', [])
            for mount in mounts:
                volume_info = {
                    'type': mount.get('Type', 'unknown'),
                    'source': mount.get('Source', ''),
                    'destination': mount.get('Destination', ''),
                    'mode': mount.get('Mode', ''),
                    'rw': mount.get('RW', True)
                }
                volumes.append(volume_info)
        except Exception as e:
            logger.warning(f"Failed to extract volumes for container {container.name}: {e}")
        
        return volumes
    
    def _extract_container_env(self, container) -> Dict[str, str]:
        """Extract environment variables from container."""
        env_vars = {}
        
        try:
            env_list = container.attrs.get('Config', {}).get('Env', [])
            for env_var in env_list:
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    # Only include OpenProject-related variables
                    if any(pattern in key.upper() for pattern in [
                        'OPENPROJECT', 'OP_', 'SECRET_KEY', 'RAILS_', 
                        'DATABASE_', 'DB_', 'POSTGRES_', 'MYSQL_',
                        'SMTP_', 'EMAIL_', 'SSL_', 'DOMAIN'
                    ]):
                        # Mask sensitive values
                        if any(sensitive in key.upper() for sensitive in [
                            'PASSWORD', 'SECRET', 'KEY', 'TOKEN'
                        ]):
                            env_vars[key] = self._mask_sensitive_value(value)
                        else:
                            env_vars[key] = value
        except Exception as e:
            logger.warning(f"Failed to extract environment for container {container.name}: {e}")
        
        return env_vars
    
    def _mask_sensitive_value(self, value: str) -> str:
        """Mask sensitive values for logging/display."""
        if not value:
            return ""
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    
    def _discover_images(self) -> List[Dict[str, Any]]:
        """Discover Docker images relevant to OpenProject."""
        if not self.docker_client:
            return []
        
        images = []
        
        try:
            for image in self.docker_client.images.list():
                # Filter for potentially relevant images
                tags = image.tags
                if not tags:
                    continue
                
                is_relevant = any(
                    keyword in tag.lower() for tag in tags
                    for keyword in [
                        'openproject', 'postgres', 'mysql', 'redis', 
                        'memcached', 'nginx', 'caddy', 'traefik'
                    ]
                )
                
                if is_relevant:
                    image_info = {
                        'id': image.id[:12],
                        'tags': tags,
                        'created': image.attrs.get('Created', ''),
                        'size': image.attrs.get('Size', 0),
                        'size_mb': round(image.attrs.get('Size', 0) / (1024 * 1024), 2),
                        'labels': image.labels,
                        'config': image.attrs.get('Config', {})
                    }
                    images.append(image_info)
        
        except Exception as e:
            logger.error(f"Failed to discover images: {e}")
        
        return images
    
    def _discover_networks(self) -> List[Dict[str, Any]]:
        """Discover Docker networks."""
        if not self.docker_client:
            return []
        
        networks = []
        
        try:
            for network in self.docker_client.networks.list():
                network_info = {
                    'id': network.id[:12],
                    'name': network.name,
                    'driver': network.attrs.get('Driver', 'unknown'),
                    'scope': network.attrs.get('Scope', 'unknown'),
                    'created': network.attrs.get('Created', ''),
                    'containers': len(network.attrs.get('Containers', {})),
                    'ipam': network.attrs.get('IPAM', {}),
                    'options': network.attrs.get('Options', {}),
                    'labels': network.attrs.get('Labels', {})
                }
                networks.append(network_info)
        
        except Exception as e:
            logger.error(f"Failed to discover networks: {e}")
        
        return networks
    
    def _discover_volumes(self) -> List[Dict[str, Any]]:
        """Discover Docker volumes."""
        if not self.docker_client:
            return []
        
        volumes = []
        
        try:
            for volume in self.docker_client.volumes.list():
                volume_info = {
                    'name': volume.name,
                    'driver': volume.attrs.get('Driver', 'unknown'),
                    'mountpoint': volume.attrs.get('Mountpoint', ''),
                    'created': volume.attrs.get('CreatedAt', ''),
                    'labels': volume.attrs.get('Labels', {}),
                    'scope': volume.attrs.get('Scope', 'unknown'),
                    'options': volume.attrs.get('Options', {})
                }
                volumes.append(volume_info)
        
        except Exception as e:
            logger.error(f"Failed to discover volumes: {e}")
        
        return volumes
    
    def _find_openproject_containers(self, containers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify containers related to OpenProject."""
        openproject_containers = []
        
        for container in containers:
            # Check if container is OpenProject-related
            is_openproject = (
                'openproject' in container['name'].lower() or
                'openproject' in container['image'].lower() or
                any('openproject' in label.lower() for label in container['labels'].values())
            )
            
            if is_openproject:
                openproject_containers.append(container)
        
        return openproject_containers
    
    def _find_database_containers(self, containers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify database containers."""
        database_containers = []
        
        db_keywords = ['postgres', 'mysql', 'mariadb', 'redis', 'memcached']
        
        for container in containers:
            is_database = any(
                keyword in container['image'].lower() or
                keyword in container['name'].lower()
                for keyword in db_keywords
            )
            
            if is_database:
                # Add database type classification
                container_copy = container.copy()
                for keyword in db_keywords:
                    if keyword in container['image'].lower():
                        container_copy['database_type'] = keyword
                        break
                database_containers.append(container_copy)
        
        return database_containers
    
    def _discover_compose_projects(self) -> List[Dict[str, Any]]:
        """Discover Docker Compose projects."""
        compose_projects = []
        
        # Look for containers with compose labels
        if not self.docker_client:
            return compose_projects
        
        try:
            projects = {}
            
            for container in self.docker_client.containers.list(all=True):
                labels = container.labels
                
                # Check for Docker Compose labels
                project_name = labels.get('com.docker.compose.project')
                if project_name:
                    if project_name not in projects:
                        projects[project_name] = {
                            'name': project_name,
                            'services': [],
                            'networks': set(),
                            'volumes': set(),
                            'containers': []
                        }
                    
                    service_name = labels.get('com.docker.compose.service', 'unknown')
                    config_hash = labels.get('com.docker.compose.config-hash', '')
                    
                    container_info = {
                        'name': container.name,
                        'service': service_name,
                        'status': container.status,
                        'config_hash': config_hash
                    }
                    
                    projects[project_name]['containers'].append(container_info)
                    projects[project_name]['services'].append(service_name)
                    
                    # Extract networks and volumes
                    networks = container.attrs.get('NetworkSettings', {}).get('Networks', {})
                    projects[project_name]['networks'].update(networks.keys())
                    
                    mounts = container.attrs.get('Mounts', [])
                    for mount in mounts:
                        if mount.get('Type') == 'volume':
                            projects[project_name]['volumes'].add(mount.get('Name', ''))
            
            # Convert sets to lists for JSON serialization
            for project_name, project_data in projects.items():
                project_data['services'] = list(set(project_data['services']))
                project_data['networks'] = list(project_data['networks'])
                project_data['volumes'] = list(project_data['volumes'])
                compose_projects.append(project_data)
        
        except Exception as e:
            logger.error(f"Failed to discover compose projects: {e}")
        
        return compose_projects
    
    def _generate_recommendations(self, docker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on Docker discovery."""
        recommendations = {
            'setup': {},
            'networking': {},
            'storage': {},
            'security': {},
            'performance': {}
        }
        
        # Setup recommendations
        if not docker_data['docker_available']:
            recommendations['setup']['error'] = "Docker is not available. Please install Docker."
            return recommendations
        
        docker_info = docker_data.get('docker_info', {})
        
        # Check Docker version
        version = docker_info.get('version', '')
        if version and version < '20.10.0':
            recommendations['setup']['warning'] = (
                f"Docker version {version} detected. Consider upgrading to 20.10.0+ for better Compose support."
            )
        
        # Memory recommendations
        memory = docker_info.get('memory', 0)
        if memory > 0:
            memory_gb = memory / (1024**3)
            if memory_gb < 2:
                recommendations['performance']['warning'] = (
                    f"Low Docker memory ({memory_gb:.1f}GB). Increase to at least 4GB for production."
                )
            elif memory_gb < 4:
                recommendations['performance']['info'] = (
                    f"Moderate Docker memory ({memory_gb:.1f}GB). Consider 8GB+ for production."
                )
        
        # Existing containers analysis
        openproject_containers = docker_data.get('openproject_containers', [])
        if openproject_containers:
            recommendations['setup']['warning'] = (
                f"Found {len(openproject_containers)} existing OpenProject container(s). "
                "Consider stopping them before deploying new configuration."
            )
        
        # Database containers analysis
        database_containers = docker_data.get('database_containers', [])
        if database_containers:
            db_types = [c.get('database_type', 'unknown') for c in database_containers]
            db_summary = ', '.join(set(db_types))
            recommendations['setup']['info'] = (
                f"Found existing database containers: {db_summary}. "
                "These can be reused for OpenProject deployment."
            )
            
            # Suggest database configuration based on existing containers
            for container in database_containers:
                if 'postgres' in container.get('database_type', ''):
                    recommendations['database'] = {
                        'suggested_adapter': 'postgresql',
                        'suggested_host': container['name'],
                        'existing_container': container['name']
                    }
                    break
                elif 'mysql' in container.get('database_type', ''):
                    recommendations['database'] = {
                        'suggested_adapter': 'mysql',
                        'suggested_host': container['name'],
                        'existing_container': container['name']
                    }
                    break
        
        # Network recommendations
        networks = docker_data.get('networks', [])
        custom_networks = [n for n in networks if n['name'] not in ['bridge', 'host', 'none']]
        if custom_networks:
            recommendations['networking']['info'] = (
                f"Found {len(custom_networks)} custom network(s). "
                "Consider using an existing network for OpenProject services."
            )
        
        # Volume recommendations
        volumes = docker_data.get('volumes', [])
        if volumes:
            openproject_volumes = [v for v in volumes if 'openproject' in v['name'].lower()]
            if openproject_volumes:
                recommendations['storage']['warning'] = (
                    f"Found {len(openproject_volumes)} existing OpenProject volume(s). "
                    "Data may be preserved from previous installations."
                )
        
        # Compose project recommendations
        compose_projects = docker_data.get('compose_projects', [])
        if compose_projects:
            recommendations['setup']['info'] = (
                f"Found {len(compose_projects)} Docker Compose project(s). "
                "Ensure proper project naming to avoid conflicts."
            )
        
        return recommendations