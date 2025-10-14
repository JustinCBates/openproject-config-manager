"""System discovery for hardware, network, and OS information."""

import os
import sys
import platform
import socket
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import json


logger = logging.getLogger(__name__)


class SystemDiscovery:
    """Discovers system information relevant to OpenProject deployment."""
    
    def __init__(self):
        """Initialize system discovery."""
        pass
    
    def discover(self) -> Dict[str, Any]:
        """
        Discover system information for OpenProject configuration.
        
        Returns:
            Dictionary containing discovered system data
        """
        logger.info("Starting system discovery")
        
        system_data = {
            'platform': self._get_platform_info(),
            'hardware': self._get_hardware_info(),
            'network': self._get_network_info(),
            'storage': self._get_storage_info(),
            'users': self._get_user_info(),
            'security': self._get_security_info(),
            'recommendations': {}
        }
        
        # Generate recommendations based on discovered data
        system_data['recommendations'] = self._generate_recommendations(system_data)
        
        logger.info("System discovery completed")
        
        return system_data
    
    def _get_platform_info(self) -> Dict[str, Any]:
        """Get platform and OS information."""
        platform_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn(),
            'python_version': sys.version,
            'python_executable': sys.executable
        }
        
        # Get Linux distribution info if available
        if platform.system().lower() == 'linux':
            try:
                import distro
                platform_info.update({
                    'distribution': distro.name(),
                    'distribution_version': distro.version(),
                    'distribution_codename': distro.codename()
                })
            except ImportError:
                # Fallback to platform.linux_distribution (deprecated)
                try:
                    dist_info = platform.linux_distribution()
                    platform_info.update({
                        'distribution': dist_info[0],
                        'distribution_version': dist_info[1],
                        'distribution_codename': dist_info[2]
                    })
                except AttributeError:
                    # Try reading /etc/os-release
                    platform_info.update(self._read_os_release())
        
        return platform_info
    
    def _read_os_release(self) -> Dict[str, str]:
        """Read OS information from /etc/os-release."""
        os_info = {}
        os_release_file = Path('/etc/os-release')
        
        if os_release_file.exists():
            try:
                with open(os_release_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            # Remove quotes
                            value = value.strip().strip('"').strip("'")
                            os_info[key.lower()] = value
            except Exception as e:
                logger.warning(f"Failed to read /etc/os-release: {e}")
        
        return os_info
    
    def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information."""
        hardware_info = {
            'cpu_count': os.cpu_count(),
            'memory': {},
            'disk': {}
        }
        
        # Memory information
        try:
            import psutil
            memory = psutil.virtual_memory()
            hardware_info['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2)
            }
            
            # Disk information
            disk_usage = psutil.disk_usage('/')
            hardware_info['disk'] = {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': (disk_usage.used / disk_usage.total) * 100,
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2)
            }
            
        except ImportError:
            logger.warning("psutil not available, limited hardware info")
            # Fallback methods for basic info
            hardware_info['memory'] = self._get_memory_fallback()
            hardware_info['disk'] = self._get_disk_fallback()
        
        return hardware_info
    
    def _get_memory_fallback(self) -> Dict[str, Any]:
        """Fallback method to get memory info without psutil."""
        memory_info = {}
        
        if platform.system().lower() == 'linux':
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            total_kb = int(line.split()[1])
                            memory_info['total'] = total_kb * 1024
                            memory_info['total_gb'] = round(total_kb / (1024**2), 2)
                        elif line.startswith('MemAvailable:'):
                            available_kb = int(line.split()[1])
                            memory_info['available'] = available_kb * 1024
                            memory_info['available_gb'] = round(available_kb / (1024**2), 2)
            except Exception as e:
                logger.warning(f"Failed to read /proc/meminfo: {e}")
        
        return memory_info
    
    def _get_disk_fallback(self) -> Dict[str, Any]:
        """Fallback method to get disk info without psutil."""
        disk_info = {}
        
        try:
            statvfs = os.statvfs('/')
            disk_info['total'] = statvfs.f_frsize * statvfs.f_blocks
            disk_info['free'] = statvfs.f_frsize * statvfs.f_bavail
            disk_info['used'] = disk_info['total'] - disk_info['free']
            disk_info['total_gb'] = round(disk_info['total'] / (1024**3), 2)
            disk_info['free_gb'] = round(disk_info['free'] / (1024**3), 2)
            disk_info['percent'] = (disk_info['used'] / disk_info['total']) * 100
        except Exception as e:
            logger.warning(f"Failed to get disk info: {e}")
        
        return disk_info
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network configuration information."""
        network_info = {
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn(),
            'interfaces': [],
            'dns_servers': [],
            'routing': {}
        }
        
        # Get network interfaces
        try:
            import netifaces
            
            for interface in netifaces.interfaces():
                if_info = {
                    'name': interface,
                    'addresses': {}
                }
                
                # Get interface addresses
                for family in netifaces.address_families:
                    addresses = netifaces.ifaddresses(interface).get(family, [])
                    if addresses:
                        family_name = {
                            netifaces.AF_INET: 'ipv4',
                            netifaces.AF_INET6: 'ipv6',
                            netifaces.AF_LINK: 'mac'
                        }.get(family, f'family_{family}')
                        if_info['addresses'][family_name] = addresses
                
                network_info['interfaces'].append(if_info)
            
            # Get default gateway
            gateways = netifaces.gateways()
            if 'default' in gateways:
                network_info['routing']['default_gateway'] = gateways['default']
        
        except ImportError:
            logger.warning("netifaces not available, limited network info")
            # Basic fallback
            network_info['interfaces'] = self._get_network_fallback()
        
        # Get DNS servers
        network_info['dns_servers'] = self._get_dns_servers()
        
        return network_info
    
    def _get_network_fallback(self) -> List[Dict[str, Any]]:
        """Fallback method to get basic network info."""
        interfaces = []
        
        try:
            # Try to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            interfaces.append({
                'name': 'primary',
                'addresses': {
                    'ipv4': [{'addr': local_ip}]
                }
            })
        except Exception as e:
            logger.warning(f"Failed to get local IP: {e}")
        
        return interfaces
    
    def _get_dns_servers(self) -> List[str]:
        """Get DNS server configuration."""
        dns_servers = []
        
        # Try to read /etc/resolv.conf on Unix systems
        if platform.system().lower() in ['linux', 'darwin']:
            resolv_conf = Path('/etc/resolv.conf')
            if resolv_conf.exists():
                try:
                    with open(resolv_conf, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('nameserver'):
                                parts = line.split()
                                if len(parts) >= 2:
                                    dns_servers.append(parts[1])
                except Exception as e:
                    logger.warning(f"Failed to read /etc/resolv.conf: {e}")
        
        return dns_servers
    
    def _get_storage_info(self) -> Dict[str, Any]:
        """Get storage and filesystem information."""
        storage_info = {
            'filesystems': [],
            'mount_points': [],
            'disk_devices': []
        }
        
        try:
            import psutil
            
            # Get disk partitions
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    fs_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2)
                    }
                    storage_info['filesystems'].append(fs_info)
                except PermissionError:
                    # Skip inaccessible mount points
                    continue
            
        except ImportError:
            logger.warning("psutil not available, limited storage info")
        
        return storage_info
    
    def _get_user_info(self) -> Dict[str, Any]:
        """Get user and permission information."""
        user_info = {
            'current_user': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
            'home_directory': os.path.expanduser('~'),
            'uid': os.getuid() if hasattr(os, 'getuid') else None,
            'gid': os.getgid() if hasattr(os, 'getgid') else None,
            'is_admin': self._check_admin_privileges(),
            'docker_access': self._check_docker_access()
        }
        
        return user_info
    
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrative privileges."""
        if platform.system().lower() == 'windows':
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                return False
        else:
            return os.getuid() == 0 if hasattr(os, 'getuid') else False
    
    def _check_docker_access(self) -> bool:
        """Check if Docker is accessible to current user."""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False
    
    def _get_security_info(self) -> Dict[str, Any]:
        """Get security-related system information."""
        security_info = {
            'firewall_detected': False,
            'selinux_status': None,
            'apparmor_status': None,
            'secure_boot': None
        }
        
        # Check for common firewalls
        firewall_commands = ['ufw', 'firewalld', 'iptables']
        for cmd in firewall_commands:
            if self._command_exists(cmd):
                security_info['firewall_detected'] = True
                break
        
        # Check SELinux status (Linux)
        if platform.system().lower() == 'linux':
            security_info['selinux_status'] = self._check_selinux()
            security_info['apparmor_status'] = self._check_apparmor()
        
        return security_info
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            subprocess.run(['which', command], 
                         capture_output=True, 
                         check=True,
                         timeout=5)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_selinux(self) -> Optional[str]:
        """Check SELinux status."""
        try:
            result = subprocess.run(['sestatus'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'SELinux status' in line:
                        return line.split(':')[1].strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
    
    def _check_apparmor(self) -> Optional[str]:
        """Check AppArmor status."""
        try:
            result = subprocess.run(['aa-status'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                return "enabled"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
    
    def _generate_recommendations(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate configuration recommendations based on system data."""
        recommendations = {
            'memory': {},
            'storage': {},
            'network': {},
            'security': {},
            'performance': {}
        }
        
        # Memory recommendations
        memory_info = system_data.get('hardware', {}).get('memory', {})
        if 'total_gb' in memory_info:
            total_gb = memory_info['total_gb']
            if total_gb < 2:
                recommendations['memory']['warning'] = "Low memory detected. Consider increasing to at least 4GB for production."
                recommendations['performance']['web_concurrency'] = 1
            elif total_gb < 4:
                recommendations['memory']['info'] = "Moderate memory available. Consider 4GB+ for production workloads."
                recommendations['performance']['web_concurrency'] = 2
            else:
                recommendations['memory']['info'] = "Sufficient memory for production deployment."
                recommendations['performance']['web_concurrency'] = min(4, int(total_gb // 2))
        
        # Storage recommendations
        disk_info = system_data.get('hardware', {}).get('disk', {})
        if 'free_gb' in disk_info:
            free_gb = disk_info['free_gb']
            if free_gb < 10:
                recommendations['storage']['warning'] = "Low disk space. Ensure at least 20GB free for production."
            elif free_gb < 50:
                recommendations['storage']['info'] = "Moderate disk space. Monitor usage in production."
            
            # Backup recommendations
            if free_gb > 100:
                recommendations['storage']['backup_location'] = "./backups"
            else:
                recommendations['storage']['backup_location'] = "/tmp/backups"
        
        # Network recommendations
        hostname = system_data.get('platform', {}).get('hostname', 'localhost')
        if hostname != 'localhost':
            recommendations['network']['suggested_domain'] = f"{hostname}.local"
        else:
            recommendations['network']['suggested_domain'] = "openproject.local"
        
        # Security recommendations
        user_info = system_data.get('users', {})
        if user_info.get('is_admin'):
            recommendations['security']['warning'] = "Running as administrator. Consider using a dedicated user for production."
        
        if not user_info.get('docker_access'):
            recommendations['security']['info'] = "Docker access not detected. Ensure Docker is installed and accessible."
        
        # Platform-specific recommendations
        platform_info = system_data.get('platform', {})
        if platform_info.get('system') == 'Linux':
            recommendations['platform'] = {
                'info': "Linux detected - optimal for Docker deployment",
                'suggested_db_port': 5432,
                'suggested_web_port': 8080
            }
        elif platform_info.get('system') == 'Darwin':
            recommendations['platform'] = {
                'info': "macOS detected - good for development",
                'suggested_db_port': 5432,
                'suggested_web_port': 8080
            }
        elif platform_info.get('system') == 'Windows':
            recommendations['platform'] = {
                'info': "Windows detected - ensure Docker Desktop is installed",
                'suggested_db_port': 5432,
                'suggested_web_port': 8080
            }
        
        return recommendations