import subprocess
import json
from typing import Dict, List
import asyncio

class KaliIntegration:
    """Integration layer for Kali Linux tools"""
    
    def __init__(self):
        self.container_name = "kali-tools"
        self.scans_path = "/root/scans"
    
    async def run_nmap_scan(self, target: str, scan_type: str = "basic") -> Dict:
        """
        Run Nmap scan from Kali container
        
        Args:
            target: IP address or hostname to scan
            scan_type: 'basic', 'intense', 'quick', 'stealth'
        """
        
        # Define scan parameters
        scan_params = {
            "basic": "-sV -sC",
            "intense": "-T4 -A -v",
            "quick": "-T4 -F",
            "stealth": "-sS -T2"
        }
        
        nmap_flags = scan_params.get(scan_type, "-sV -sC")
        output_file = f"{self.scans_path}/nmap_{target.replace('.', '_')}.xml"
        
        # Build command
        cmd = [
            "docker", "exec", self.container_name,
            "nmap", nmap_flags, "-oX", output_file, target
        ]
        
        print(f"[+] Running Nmap {scan_type} scan on {target}...")
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "status": "success",
                    "tool": "nmap",
                    "target": target,
                    "scan_type": scan_type,
                    "output": stdout.decode(),
                    "output_file": output_file
                }
            else:
                return {
                    "status": "error",
                    "tool": "nmap",
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "tool": "nmap",
                "error": str(e)
            }
    
    async def run_nikto_scan(self, target_url: str) -> Dict:
        """
        Run Nikto web server scan
        
        Args:
            target_url: URL to scan (e.g., http://example.com)
        """
        
        output_file = f"{self.scans_path}/nikto_{target_url.replace('://', '_').replace('/', '_')}.txt"
        
        cmd = [
            "docker", "exec", self.container_name,
            "nikto", "-h", target_url, "-o", output_file
        ]
        
        print(f"[+] Running Nikto scan on {target_url}...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success",
                "tool": "nikto",
                "target": target_url,
                "output": stdout.decode(),
                "output_file": output_file
            }
            
        except Exception as e:
            return {
                "status": "error",
                "tool": "nikto",
                "error": str(e)
            }
    
    async def run_sqlmap_scan(self, target_url: str, params: str = None) -> Dict:
        """
        Run SQLMap for SQL injection testing
        
        Args:
            target_url: URL to test
            params: Specific parameter to test (optional)
        """
        
        cmd = [
            "docker", "exec", self.container_name,
            "sqlmap", "-u", target_url, "--batch", "--level=1", "--risk=1"
        ]
        
        if params:
            cmd.extend(["-p", params])
        
        print(f"[+] Running SQLMap on {target_url}...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success",
                "tool": "sqlmap",
                "target": target_url,
                "output": stdout.decode()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "tool": "sqlmap",
                "error": str(e)
            }
    
    async def run_dirb_scan(self, target_url: str, wordlist: str = None) -> Dict:
        """
        Run DIRB directory bruteforcing
        
        Args:
            target_url: Base URL to scan
            wordlist: Path to wordlist (optional, uses default if None)
        """
        
        output_file = f"{self.scans_path}/dirb_{target_url.replace('://', '_').replace('/', '_')}.txt"
        
        cmd = [
            "docker", "exec", self.container_name,
            "dirb", target_url
        ]
        
        if wordlist:
            cmd.append(wordlist)
        
        cmd.extend(["-o", output_file])
        
        print(f"[+] Running DIRB on {target_url}...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success",
                "tool": "dirb",
                "target": target_url,
                "output": stdout.decode(),
                "output_file": output_file
            }
            
        except Exception as e:
            return {
                "status": "error",
                "tool": "dirb",
                "error": str(e)
            }
    
    async def run_custom_command(self, command: str) -> Dict:
        """
        Run any custom command in Kali container
        
        Args:
            command: Shell command to execute
        """
        
        cmd = [
            "docker", "exec", self.container_name,
            "bash", "-c", command
        ]
        
        print(f"[+] Running custom command: {command}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success",
                "tool": "custom",
                "command": command,
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "tool": "custom",
                "error": str(e)
            }