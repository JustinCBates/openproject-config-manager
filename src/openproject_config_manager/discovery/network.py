"""Network discovery for OpenProject deployment configuration."""

import json
import logging
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class NetworkDiscovery:
    """Advanced network discovery for OpenProject deployment."""

    # Common ports used by OpenProject and related services
    OPENPROJECT_PORTS = {
        "web": [80, 443, 8080, 8443, 3000],
        "database": [5432, 3306, 5433],
        "cache": [6379, 11211],
        "email": [25, 587, 465, 993, 995],
        "ldap": [389, 636],
        "ssh": [22],
        "docker": [2375, 2376, 2377],
    }

    def __init__(self):
        """Initialize network discovery."""
        self.hostname = socket.gethostname()
        self.fqdn = socket.getfqdn()

    def discover(self) -> Dict[str, Any]:
        """
        Perform comprehensive network discovery for OpenProject deployment.

        Returns:
            Dictionary containing network discovery results
        """
        logger.info("Starting network discovery")

        network_data = {
            "basic_info": self._get_basic_network_info(),
            "interfaces": self._discover_interfaces(),
            "connectivity": self._test_connectivity(),
            "port_analysis": self._analyze_ports(),
            "dns_analysis": self._analyze_dns(),
            "routing": self._analyze_routing(),
            "docker_networks": self._discover_docker_networks(),
            "security": self._analyze_network_security(),
            "conflicts": self._detect_conflicts(),
            "recommendations": {},
        }

        # Generate network-specific recommendations
        network_data["recommendations"] = self._generate_network_recommendations(network_data)

        logger.info("Network discovery completed")

        return network_data

    def _get_basic_network_info(self) -> Dict[str, Any]:
        """Get basic network information."""
        return {
            "hostname": self.hostname,
            "fqdn": self.fqdn,
            "domain": self.fqdn.split(".", 1)[1] if "." in self.fqdn else None,
            "reverse_dns": self._get_reverse_dns(),
            "public_ip": self._get_public_ip(),
            "local_ip": self._get_local_ip(),
        }

    def _discover_interfaces(self) -> List[Dict[str, Any]]:
        """Discover network interfaces and their configuration."""
        interfaces = []

        try:
            import netifaces

            for interface in netifaces.interfaces():
                if_data = {
                    "name": interface,
                    "addresses": {},
                    "status": "unknown",
                    "mtu": None,
                    "type": self._get_interface_type(interface),
                }

                # Get addresses for each family
                for family in netifaces.address_families:
                    addresses = netifaces.ifaddresses(interface).get(family, [])
                    if addresses:
                        family_name = {
                            netifaces.AF_INET: "ipv4",
                            netifaces.AF_INET6: "ipv6",
                            netifaces.AF_LINK: "mac",
                        }.get(family, f"family_{family}")
                        if_data["addresses"][family_name] = addresses

                # Determine if interface is up
                if_data["status"] = self._get_interface_status(interface)

                interfaces.append(if_data)

        except ImportError:
            logger.warning("netifaces not available, using fallback interface discovery")
            interfaces = self._discover_interfaces_fallback()

        return interfaces

    def _test_connectivity(self) -> Dict[str, Any]:
        """Test network connectivity to important services."""
        connectivity = {
            "internet": False,
            "dns": False,
            "docker_registry": False,
            "package_managers": {},
            "external_services": {},
        }

        # Test internet connectivity
        connectivity["internet"] = self._test_internet_connection()

        # Test DNS resolution
        connectivity["dns"] = self._test_dns_resolution()

        # Test Docker registry access
        connectivity["docker_registry"] = self._test_docker_registry()

        # Test package manager connectivity
        connectivity["package_managers"] = self._test_package_managers()

        # Test external service connectivity
        connectivity["external_services"] = self._test_external_services()

        return connectivity

    def _analyze_ports(self) -> Dict[str, Any]:
        """Analyze port usage and availability."""
        port_analysis = {
            "listening_ports": self._get_listening_ports(),
            "openproject_port_conflicts": {},
            "recommended_ports": {},
            "available_ports": [],
        }

        # Check for conflicts with OpenProject ports
        listening_ports = port_analysis["listening_ports"]

        for service, ports in self.OPENPROJECT_PORTS.items():
            conflicts = []
            available = []

            for port in ports:
                if self._is_port_in_use(port, listening_ports):
                    process_info = self._get_port_process_info(port)
                    conflicts.append({"port": port, "process": process_info})
                else:
                    available.append(port)

            port_analysis["openproject_port_conflicts"][service] = conflicts
            if available:
                port_analysis["recommended_ports"][service] = available[0]

        # Find available ports in common ranges
        port_analysis["available_ports"] = self._find_available_ports()

        return port_analysis

    def _analyze_dns(self) -> Dict[str, Any]:
        """Analyze DNS configuration and resolution."""
        dns_analysis = {
            "servers": self._get_dns_servers(),
            "resolution_test": {},
            "reverse_dns": {},
            "performance": {},
        }

        # Test DNS resolution performance
        dns_analysis["resolution_test"] = self._test_dns_performance()

        # Test reverse DNS for local IP
        local_ip = self._get_local_ip()
        if local_ip:
            dns_analysis["reverse_dns"][local_ip] = self._resolve_reverse_dns(local_ip)

        return dns_analysis

    def _analyze_routing(self) -> Dict[str, Any]:
        """Analyze network routing configuration."""
        routing = {"default_gateway": None, "routes": [], "reachability": {}}

        try:
            import netifaces

            gateways = netifaces.gateways()
            if "default" in gateways:
                routing["default_gateway"] = gateways["default"]
        except ImportError:
            routing["default_gateway"] = self._get_default_gateway_fallback()

        # Get routing table
        routing["routes"] = self._get_routing_table()

        # Test reachability to important destinations
        routing["reachability"] = self._test_network_reachability()

        return routing

    def _discover_docker_networks(self) -> List[Dict[str, Any]]:
        """Discover existing Docker networks."""
        docker_networks = []

        try:
            import docker

            client = docker.from_env()

            for network in client.networks.list():
                network_info = {
                    "id": network.id[:12],
                    "name": network.name,
                    "driver": network.attrs.get("Driver", "unknown"),
                    "scope": network.attrs.get("Scope", "local"),
                    "subnet": None,
                    "gateway": None,
                    "containers": [],
                }

                # Get IPAM configuration
                ipam = network.attrs.get("IPAM", {})
                if ipam.get("Config"):
                    config = ipam["Config"][0] if ipam["Config"] else {}
                    network_info["subnet"] = config.get("Subnet")
                    network_info["gateway"] = config.get("Gateway")

                # Get connected containers
                containers = network.attrs.get("Containers", {})
                for container_id, container_info in containers.items():
                    network_info["containers"].append(
                        {
                            "id": container_id[:12],
                            "name": container_info.get("Name", "unknown"),
                            "ipv4": container_info.get("IPv4Address", "").split("/")[0],
                        }
                    )

                docker_networks.append(network_info)

        except Exception as e:
            logger.warning(f"Failed to discover Docker networks: {e}")

        return docker_networks

    def _analyze_network_security(self) -> Dict[str, Any]:
        """Analyze network security configuration."""
        security = {
            "firewall": self._detect_firewall(),
            "open_ports": [],
            "listening_services": [],
            "security_warnings": [],
        }

        # Analyze listening services for security concerns
        listening_ports = self._get_listening_ports()

        for port_info in listening_ports:
            port = port_info.get("port")
            protocol = port_info.get("protocol", "tcp")

            # Check for potentially insecure services
            if port in [21, 23, 80, 139, 445]:  # FTP, Telnet, HTTP, SMB
                security["security_warnings"].append(
                    {
                        "type": "insecure_service",
                        "port": port,
                        "protocol": protocol,
                        "description": f"Potentially insecure service on port {port}",
                    }
                )

            # Check for non-standard SSH ports
            if port != 22 and port_info.get("service") == "ssh":
                security["security_warnings"].append(
                    {
                        "type": "non_standard_ssh",
                        "port": port,
                        "description": f"SSH running on non-standard port {port}",
                    }
                )

        return security

    def _detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect potential network conflicts for OpenProject deployment."""
        conflicts = []

        # Port conflicts
        for service, ports in self.OPENPROJECT_PORTS.items():
            for port in ports:
                if self._is_port_in_use(port):
                    process_info = self._get_port_process_info(port)
                    conflicts.append(
                        {
                            "type": "port_conflict",
                            "service": service,
                            "port": port,
                            "conflicting_process": process_info,
                            "severity": "high" if service == "web" else "medium",
                        }
                    )

        # Docker network conflicts
        docker_networks = self._discover_docker_networks()
        for network in docker_networks:
            if network["name"] in ["openproject", "openproject-network"]:
                conflicts.append(
                    {
                        "type": "docker_network_conflict",
                        "network_name": network["name"],
                        "network_id": network["id"],
                        "severity": "medium",
                    }
                )

        # Hostname conflicts
        if self.hostname == "localhost" or self.hostname.startswith("ip-"):
            conflicts.append(
                {
                    "type": "hostname_issue",
                    "hostname": self.hostname,
                    "description": "Generic or auto-generated hostname detected",
                    "severity": "low",
                }
            )

        return conflicts

    def _generate_network_recommendations(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate network configuration recommendations."""
        recommendations = {"ports": {}, "hostname": {}, "dns": {}, "security": {}, "docker": {}}

        # Port recommendations
        port_analysis = network_data.get("port_analysis", {})
        recommended_ports = port_analysis.get("recommended_ports", {})

        if "web" in recommended_ports:
            recommendations["ports"]["web"] = {
                "recommended": recommended_ports["web"],
                "alternatives": [
                    p for p in self.OPENPROJECT_PORTS["web"] if p != recommended_ports["web"]
                ],
            }
        else:
            # Find alternative ports if all default ports are taken
            available_ports = port_analysis.get("available_ports", [])
            web_alternatives = [p for p in available_ports if 8000 <= p <= 9000]
            if web_alternatives:
                recommendations["ports"]["web"] = {
                    "recommended": web_alternatives[0],
                    "note": "All standard web ports are in use",
                }

        # Hostname recommendations
        basic_info = network_data.get("basic_info", {})
        if basic_info.get("hostname") == "localhost":
            recommendations["hostname"] = {
                "suggestion": "openproject-server",
                "note": "Consider setting a meaningful hostname",
            }

        # DNS recommendations
        dns_analysis = network_data.get("dns_analysis", {})
        if not dns_analysis.get("resolution_test", {}).get("success", False):
            recommendations["dns"] = {
                "suggestion": "Configure reliable DNS servers",
                "recommended_dns": ["8.8.8.8", "1.1.1.1"],
            }

        # Security recommendations
        security = network_data.get("security", {})
        if not security.get("firewall", {}).get("active", False):
            recommendations["security"]["firewall"] = {
                "suggestion": "Enable firewall for production deployment",
                "note": "Consider using ufw, firewalld, or iptables",
            }

        # Docker network recommendations
        docker_networks = network_data.get("docker_networks", [])
        if not any(net["name"] == "openproject" for net in docker_networks):
            recommendations["docker"]["network"] = {
                "suggestion": "Create dedicated Docker network for OpenProject",
                "command": "docker network create openproject --driver bridge",
            }

        return recommendations

    # Helper methods

    def _get_reverse_dns(self) -> Optional[str]:
        """Get reverse DNS for local IP."""
        local_ip = self._get_local_ip()
        if local_ip:
            return self._resolve_reverse_dns(local_ip)
        return None

    def _get_public_ip(self) -> Optional[str]:
        """Get public IP address."""
        try:
            import urllib.request

            response = urllib.request.urlopen("https://ifconfig.me/ip", timeout=5)
            return response.read().decode("utf-8").strip()
        except Exception:
            try:
                # Fallback method
                response = urllib.request.urlopen("https://api.ipify.org", timeout=5)
                return response.read().decode("utf-8").strip()
            except Exception:
                logger.warning("Failed to determine public IP")
                return None

    def _get_local_ip(self) -> Optional[str]:
        """Get local IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return None

    def _get_interface_type(self, interface: str) -> str:
        """Determine interface type."""
        if interface.startswith("lo"):
            return "loopback"
        elif interface.startswith(("eth", "en")):
            return "ethernet"
        elif interface.startswith(("wlan", "wifi", "wl")):
            return "wireless"
        elif interface.startswith("docker"):
            return "docker"
        elif interface.startswith("br-"):
            return "bridge"
        else:
            return "unknown"

    def _get_interface_status(self, interface: str) -> str:
        """Get interface status."""
        try:
            result = subprocess.run(
                ["ip", "link", "show", interface], capture_output=True, text=True, timeout=5
            )
            if "UP" in result.stdout:
                return "up"
            else:
                return "down"
        except Exception:
            return "unknown"

    def _discover_interfaces_fallback(self) -> List[Dict[str, Any]]:
        """Fallback interface discovery method."""
        interfaces = []

        try:
            # Try ip command
            result = subprocess.run(
                ["ip", "addr", "show"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Parse ip output (simplified)
                interfaces.append(
                    {
                        "name": "primary",
                        "addresses": {"ipv4": [{"addr": self._get_local_ip()}]},
                        "status": "up",
                        "type": "ethernet",
                    }
                )
        except Exception:
            # Most basic fallback
            interfaces.append(
                {
                    "name": "unknown",
                    "addresses": {"ipv4": [{"addr": self._get_local_ip() or "127.0.0.1"}]},
                    "status": "unknown",
                    "type": "unknown",
                }
            )

        return interfaces

    def _test_internet_connection(self) -> bool:
        """Test internet connectivity."""
        test_hosts = ["8.8.8.8", "1.1.1.1", "google.com"]

        for host in test_hosts:
            try:
                socket.create_connection((host, 80), timeout=5)
                return True
            except Exception:
                continue

        return False

    def _test_dns_resolution(self) -> bool:
        """Test DNS resolution."""
        test_domains = ["google.com", "github.com", "docker.io"]

        for domain in test_domains:
            try:
                socket.gethostbyname(domain)
                return True
            except Exception:
                continue

        return False

    def _test_docker_registry(self) -> bool:
        """Test Docker registry connectivity."""
        try:
            socket.create_connection(("registry-1.docker.io", 443), timeout=10)
            return True
        except Exception:
            return False

    def _test_package_managers(self) -> Dict[str, bool]:
        """Test package manager connectivity."""
        managers = {}

        # Test apt (Debian/Ubuntu)
        if self._command_exists("apt"):
            managers["apt"] = self._test_url_connectivity("archive.ubuntu.com", 80)

        # Test yum/dnf (RedHat/CentOS/Fedora)
        if self._command_exists("yum") or self._command_exists("dnf"):
            managers["yum"] = self._test_url_connectivity("mirror.centos.org", 80)

        return managers

    def _test_external_services(self) -> Dict[str, bool]:
        """Test connectivity to external services."""
        services = {}

        # GitHub (for code/container pulls)
        services["github"] = self._test_url_connectivity("github.com", 443)

        # Docker Hub
        services["docker_hub"] = self._test_url_connectivity("hub.docker.com", 443)

        # Let's Encrypt (for SSL certificates)
        services["letsencrypt"] = self._test_url_connectivity("acme-v02.api.letsencrypt.org", 443)

        return services

    def _test_url_connectivity(self, host: str, port: int) -> bool:
        """Test connectivity to a specific host:port."""
        try:
            socket.create_connection((host, port), timeout=5)
            return True
        except Exception:
            return False

    def _get_listening_ports(self) -> List[Dict[str, Any]]:
        """Get list of listening ports."""
        ports = []

        try:
            # Try ss command first (modern)
            result = subprocess.run(["ss", "-tuln"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                ports = self._parse_ss_output(result.stdout)
            else:
                # Fallback to netstat
                result = subprocess.run(
                    ["netstat", "-tuln"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    ports = self._parse_netstat_output(result.stdout)
        except Exception as e:
            logger.warning(f"Failed to get listening ports: {e}")

        return ports

    def _parse_ss_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse ss command output."""
        ports = []

        for line in output.split("\n")[1:]:  # Skip header
            if line.strip() and "LISTEN" in line:
                parts = line.split()
                if len(parts) >= 4:
                    local_addr = parts[3]
                    if ":" in local_addr:
                        port_str = local_addr.rsplit(":", 1)[1]
                        try:
                            port = int(port_str)
                            protocol = parts[0].lower()
                            ports.append(
                                {
                                    "port": port,
                                    "protocol": protocol,
                                    "address": local_addr,
                                    "state": "LISTEN",
                                }
                            )
                        except ValueError:
                            continue

        return ports

    def _parse_netstat_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse netstat command output."""
        ports = []

        for line in output.split("\n"):
            if "LISTEN" in line:
                parts = line.split()
                if len(parts) >= 4:
                    local_addr = parts[3]
                    if ":" in local_addr:
                        port_str = local_addr.rsplit(":", 1)[1]
                        try:
                            port = int(port_str)
                            protocol = parts[0].lower()
                            ports.append(
                                {
                                    "port": port,
                                    "protocol": protocol,
                                    "address": local_addr,
                                    "state": "LISTEN",
                                }
                            )
                        except ValueError:
                            continue

        return ports

    def _is_port_in_use(self, port: int, listening_ports: Optional[List] = None) -> bool:
        """Check if a port is in use."""
        if listening_ports is None:
            listening_ports = self._get_listening_ports()

        return any(p.get("port") == port for p in listening_ports)

    def _get_port_process_info(self, port: int) -> Dict[str, Any]:
        """Get information about process using a port."""
        try:
            # Try lsof first
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:  # Skip header
                    parts = lines[1].split()
                    return {
                        "command": parts[0] if len(parts) > 0 else "unknown",
                        "pid": parts[1] if len(parts) > 1 else "unknown",
                        "user": parts[2] if len(parts) > 2 else "unknown",
                    }
        except Exception:
            pass

        try:
            # Fallback to ss with process info
            result = subprocess.run(["ss", "-tulnp"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if f":{port}" in line and "LISTEN" in line:
                        # Extract process info from ss output
                        if "users:" in line:
                            process_part = line.split("users:")[1].strip()
                            return {"process_info": process_part}
        except Exception:
            pass

        return {"command": "unknown", "pid": "unknown", "user": "unknown"}

    def _find_available_ports(
        self, start: int = 8000, end: int = 9000, count: int = 10
    ) -> List[int]:
        """Find available ports in a given range."""
        available = []
        listening_ports = self._get_listening_ports()
        used_ports = {p.get("port") for p in listening_ports}

        for port in range(start, end + 1):
            if port not in used_ports and len(available) < count:
                # Double-check by trying to bind
                if self._test_port_availability(port):
                    available.append(port)

        return available

    def _test_port_availability(self, port: int) -> bool:
        """Test if a port is available by trying to bind to it."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("localhost", port))
            sock.close()
            return True
        except Exception:
            return False

    def _get_dns_servers(self) -> List[str]:
        """Get configured DNS servers."""
        dns_servers = []

        # Try reading /etc/resolv.conf
        resolv_conf = Path("/etc/resolv.conf")
        if resolv_conf.exists():
            try:
                with open(resolv_conf, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("nameserver"):
                            parts = line.split()
                            if len(parts) >= 2:
                                dns_servers.append(parts[1])
            except Exception as e:
                logger.warning(f"Failed to read /etc/resolv.conf: {e}")

        return dns_servers

    def _test_dns_performance(self) -> Dict[str, Any]:
        """Test DNS resolution performance."""
        test_domains = ["google.com", "github.com"]
        results = {"success": False, "average_time": None, "failed_domains": []}

        times = []

        for domain in test_domains:
            start_time = time.time()
            try:
                socket.gethostbyname(domain)
                end_time = time.time()
                times.append(end_time - start_time)
            except Exception:
                results["failed_domains"].append(domain)

        if times:
            results["success"] = True
            results["average_time"] = sum(times) / len(times)

        return results

    def _resolve_reverse_dns(self, ip: str) -> Optional[str]:
        """Resolve reverse DNS for an IP address."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return None

    def _get_default_gateway_fallback(self) -> Optional[str]:
        """Get default gateway using fallback methods."""
        try:
            # Try route command
            result = subprocess.run(["route", "-n"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.startswith("0.0.0.0"):
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1]
        except Exception:
            pass

        try:
            # Try ip route
            result = subprocess.run(
                ["ip", "route", "show", "default"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.split()
                if "via" in parts:
                    via_index = parts.index("via")
                    if via_index + 1 < len(parts):
                        return parts[via_index + 1]
        except Exception:
            pass

        return None

    def _get_routing_table(self) -> List[Dict[str, Any]]:
        """Get routing table information."""
        routes = []

        try:
            result = subprocess.run(
                ["ip", "route", "show"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.strip():
                        # Parse route line (simplified)
                        parts = line.split()
                        if parts:
                            route = {
                                "destination": parts[0],
                                "via": None,
                                "dev": None,
                                "metric": None,
                            }

                            # Extract via, dev, metric if present
                            for i, part in enumerate(parts):
                                if part == "via" and i + 1 < len(parts):
                                    route["via"] = parts[i + 1]
                                elif part == "dev" and i + 1 < len(parts):
                                    route["dev"] = parts[i + 1]
                                elif part == "metric" and i + 1 < len(parts):
                                    route["metric"] = parts[i + 1]

                            routes.append(route)
        except Exception as e:
            logger.warning(f"Failed to get routing table: {e}")

        return routes

    def _test_network_reachability(self) -> Dict[str, bool]:
        """Test reachability to important network destinations."""
        destinations = {
            "default_gateway": self._get_default_gateway_fallback(),
            "dns_servers": self._get_dns_servers(),
            "public_dns": ["8.8.8.8", "1.1.1.1"],
        }

        reachability = {}

        # Test default gateway
        if destinations["default_gateway"]:
            reachability["default_gateway"] = self._ping_host(destinations["default_gateway"])

        # Test DNS servers
        for dns in destinations["dns_servers"][:2]:  # Test first 2 DNS servers
            reachability[f"dns_{dns}"] = self._ping_host(dns)

        # Test public DNS
        for dns in destinations["public_dns"]:
            reachability[f"public_dns_{dns}"] = self._ping_host(dns)

        return reachability

    def _ping_host(self, host: str, count: int = 1, timeout: int = 5) -> bool:
        """Ping a host to test reachability."""
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), "-W", str(timeout), host],
                capture_output=True,
                text=True,
                timeout=timeout + 2,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _detect_firewall(self) -> Dict[str, Any]:
        """Detect firewall configuration."""
        firewall = {"type": None, "active": False, "status": "unknown"}

        # Check for ufw
        if self._command_exists("ufw"):
            try:
                result = subprocess.run(
                    ["ufw", "status"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    firewall["type"] = "ufw"
                    firewall["active"] = "Status: active" in result.stdout
                    firewall["status"] = result.stdout.strip()
            except Exception:
                pass

        # Check for firewalld
        elif self._command_exists("firewall-cmd"):
            try:
                result = subprocess.run(
                    ["firewall-cmd", "--state"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    firewall["type"] = "firewalld"
                    firewall["active"] = "running" in result.stdout.lower()
                    firewall["status"] = result.stdout.strip()
            except Exception:
                pass

        # Check for iptables
        elif self._command_exists("iptables"):
            try:
                result = subprocess.run(
                    ["iptables", "-L", "-n"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    firewall["type"] = "iptables"
                    # Basic check - if there are rules beyond default, firewall is likely active
                    lines = result.stdout.split("\n")
                    firewall["active"] = (
                        len(
                            [
                                l
                                for l in lines
                                if l.strip()
                                and not l.startswith("Chain")
                                and not l.startswith("target")
                            ]
                        )
                        > 0
                    )
            except Exception:
                pass

        return firewall

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists."""
        try:
            subprocess.run(["which", command], capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
