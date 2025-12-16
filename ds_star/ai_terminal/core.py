"""
AI Research Terminal - Multi-Provider LLM Interface with File System Access
Supports: OpenAI (GPT-5.1, GPT-4o), Anthropic (Claude), Google (Gemini), xAI (Grok)
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class AITerminal:
    """Multi-provider AI terminal with file system access capabilities."""
    
    BLOCKED_PATHS = [
        '.cache',
        '.env',
        '.env.local',
        '.env.development',
        '.env.production',
        'secrets',
        '.git',
        '.ssh',
        '.gnupg',
        '.netrc',
        '.npmrc',
        '.pypirc',
        '.pythonlibs',
        '.upm',
        '.replit',
    ]
    
    BLOCKED_PATTERNS = [
        'api_key',
        'secret',
        'password',
        'credential',
        'token',
        '.pem',
        '.key',
    ]
    
    PROVIDERS = {
        "openai": {
            "name": "OpenAI",
            "models": ["gpt-5.1", "gpt-5", "gpt-5-mini", "gpt-4.1", "gpt-4o", "gpt-4o-mini", "o4-mini", "o3", "o3-mini"],
            "default": "gpt-4o-mini"
        },
        "anthropic": {
            "name": "Anthropic",
            "models": ["claude-opus-4-1", "claude-sonnet-4-5", "claude-haiku-4-5"],
            "default": "claude-sonnet-4-5"
        },
        "gemini": {
            "name": "Google Gemini",
            "models": ["gemini-3-pro-preview", "gemini-2.5-pro", "gemini-2.5-flash"],
            "default": "gemini-2.5-flash"
        }
    }
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.current_provider = "openai"
        self.current_model = "gpt-4o-mini"
        self.workspace_root = Path(os.getcwd())
    
    def _normalize_and_validate_path(self, path: str) -> tuple[Optional[Path], Optional[str]]:
        """
        Normalize a path and validate it's within workspace boundaries.
        Returns (resolved_path, None) if valid, or (None, error_message) if invalid.
        """
        try:
            target = (self.workspace_root / path).resolve()
            
            try:
                target.relative_to(self.workspace_root.resolve())
            except ValueError:
                return None, "Access denied: Path traversal detected"
            
            rel_path = str(target.relative_to(self.workspace_root.resolve()))
            if self._is_path_blocked(rel_path):
                return None, "Access denied: This path contains sensitive information"
            
            return target, None
        except Exception as e:
            return None, f"Invalid path: {str(e)}"
    
    def _is_path_blocked(self, path: str) -> bool:
        """Check if a path should be blocked for security reasons."""
        path_lower = path.lower()
        path_parts = Path(path).parts
        
        for blocked in self.BLOCKED_PATHS:
            blocked_lower = blocked.lower()
            if path_lower.startswith(blocked_lower + '/') or path_lower.startswith(blocked_lower + '\\'):
                return True
            if path_lower == blocked_lower:
                return True
            for part in path_parts:
                if part.lower() == blocked_lower.lstrip('.'):
                    return True
                if part.lower() == blocked_lower:
                    return True
        
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in path_lower:
                return True
        
        return False
        
    def get_available_providers(self) -> Dict[str, Any]:
        """Get all available AI providers and their models."""
        return self.PROVIDERS
    
    def set_provider(self, provider: str, model: str = None) -> Dict[str, Any]:
        """Set the current AI provider and model."""
        if provider not in self.PROVIDERS:
            return {"success": False, "error": f"Unknown provider: {provider}"}
        
        self.current_provider = provider
        if model:
            if model not in self.PROVIDERS[provider]["models"]:
                return {"success": False, "error": f"Unknown model: {model} for provider {provider}"}
            self.current_model = model
        else:
            self.current_model = self.PROVIDERS[provider]["default"]
        
        return {
            "success": True,
            "provider": provider,
            "model": self.current_model
        }
    
    def list_files(self, path: str = ".") -> Dict[str, Any]:
        """List files in the specified directory."""
        try:
            target_path, error = self._normalize_and_validate_path(path)
            if error:
                return {"success": False, "error": error}
            
            if not target_path.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            if not target_path.is_dir():
                return {"success": False, "error": f"Not a directory: {path}"}
            
            files = []
            for item in sorted(target_path.iterdir()):
                try:
                    item_rel_path = str(item.relative_to(self.workspace_root.resolve()))
                    if self._is_path_blocked(item_rel_path):
                        continue
                    
                    stat = item.stat()
                    files.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except (PermissionError, OSError):
                    continue
            
            return {
                "success": True,
                "path": str(target_path.relative_to(self.workspace_root.resolve())),
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, path: str, max_lines: int = 500) -> Dict[str, Any]:
        """Read contents of a file."""
        try:
            target_path, error = self._normalize_and_validate_path(path)
            if error:
                return {"success": False, "error": error}
            
            if not target_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            if not target_path.is_file():
                return {"success": False, "error": f"Not a file: {path}"}
            
            with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            truncated = len(lines) > max_lines
            content = ''.join(lines[:max_lines])
            
            return {
                "success": True,
                "path": path,
                "content": content,
                "lines": len(lines),
                "truncated": truncated,
                "size": target_path.stat().st_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_files(self, pattern: str, path: str = ".") -> Dict[str, Any]:
        """Search for files matching a pattern."""
        try:
            target_path, error = self._normalize_and_validate_path(path)
            if error:
                return {"success": False, "error": error}
            
            if not target_path.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            matches = list(target_path.rglob(pattern))
            files = []
            for match in matches[:100]:
                try:
                    rel_path = str(match.relative_to(self.workspace_root.resolve()))
                    if self._is_path_blocked(rel_path):
                        continue
                    files.append({
                        "path": rel_path,
                        "type": "directory" if match.is_dir() else "file",
                        "size": match.stat().st_size if match.is_file() else None
                    })
                except (PermissionError, OSError, ValueError):
                    pass
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": files,
                "count": len(files),
                "truncated": len(matches) > 100
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_file_tree(self, path: str = ".", max_depth: int = 3) -> Dict[str, Any]:
        """Get a tree view of the file system."""
        try:
            target_path, error = self._normalize_and_validate_path(path)
            if error:
                return {"success": False, "error": error}
            
            if not target_path.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            workspace_resolved = self.workspace_root.resolve()
            
            def build_tree(p: Path, depth: int) -> Optional[Dict[str, Any]]:
                try:
                    rel_path = str(p.relative_to(workspace_resolved))
                except ValueError:
                    return None
                
                if self._is_path_blocked(rel_path):
                    return None
                
                if depth > max_depth:
                    return {"name": p.name, "type": "directory", "truncated": True}
                
                if p.is_file():
                    return {
                        "name": p.name,
                        "type": "file",
                        "size": p.stat().st_size
                    }
                
                children = []
                try:
                    items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                    for item in items[:50]:
                        if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv']:
                            continue
                        child = build_tree(item, depth + 1)
                        if child:
                            children.append(child)
                except PermissionError:
                    pass
                
                return {
                    "name": p.name,
                    "type": "directory",
                    "children": children
                }
            
            tree = build_tree(target_path, 0)
            return {"success": True, "tree": tree}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def chat_openai(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """Chat using OpenAI models via Replit AI Integrations."""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
                base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
            )
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system",
                    "content": "You are a helpful AI research assistant with access to the user's file system. Help them analyze code, research trading strategies, and provide insights."
                })
            
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            
            messages.append({"role": "user", "content": message})
            
            response = client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content
            
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return {
                "success": True,
                "response": assistant_message,
                "model": self.current_model,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def chat_anthropic(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """Chat using Anthropic Claude models. Prefers user's own API key if provided."""
        try:
            import anthropic
            
            # Prefer user's own API key for history tracking, fallback to Replit integration
            user_key = os.environ.get("ANTHROPIC_API_KEY")
            if user_key:
                client = anthropic.Anthropic(api_key=user_key)
            else:
                client = anthropic.Anthropic(
                    api_key=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY"),
                    base_url=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")
                )
            
            messages = []
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            messages.append({"role": "user", "content": message})
            
            sys_prompt = system_prompt or "You are a helpful AI research assistant with access to the user's file system. Help them analyze code, research trading strategies, and provide insights."
            
            response = client.messages.create(
                model=self.current_model,
                max_tokens=4096,
                system=sys_prompt,
                messages=messages
            )
            
            assistant_message = response.content[0].text
            
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return {
                "success": True,
                "response": assistant_message,
                "model": self.current_model,
                "provider": "anthropic",
                "usage": {
                    "input_tokens": response.usage.input_tokens if response.usage else 0,
                    "output_tokens": response.usage.output_tokens if response.usage else 0
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def chat_gemini(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """Chat using Google Gemini models via Replit AI Integrations."""
        try:
            from google import genai
            
            client = genai.Client(
                api_key=os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY"),
                http_options={"api_version": "v1alpha"}
            )
            
            sys_prompt = system_prompt or "You are a helpful AI research assistant with access to the user's file system. Help them analyze code, research trading strategies, and provide insights."
            
            full_prompt = f"{sys_prompt}\n\nConversation history:\n"
            for msg in self.conversation_history[-10:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role}: {msg['content']}\n\n"
            full_prompt += f"User: {message}\n\nAssistant:"
            
            response = client.models.generate_content(
                model=self.current_model,
                contents=full_prompt
            )
            
            assistant_message = response.text
            
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return {
                "success": True,
                "response": assistant_message,
                "model": self.current_model,
                "provider": "gemini"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def chat(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """Send a chat message using the current provider."""
        if self.current_provider == "openai":
            return self.chat_openai(message, system_prompt)
        elif self.current_provider == "anthropic":
            return self.chat_anthropic(message, system_prompt)
        elif self.current_provider == "gemini":
            return self.chat_gemini(message, system_prompt)
        else:
            return {"success": False, "error": f"Unknown provider: {self.current_provider}"}
    
    def clear_history(self) -> Dict[str, Any]:
        """Clear conversation history."""
        self.conversation_history = []
        return {"success": True, "message": "Conversation history cleared"}
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history
    
    def analyze_file(self, path: str, question: str = None) -> Dict[str, Any]:
        """Read a file and analyze it with the current AI model."""
        file_result = self.read_file(path)
        if not file_result["success"]:
            return file_result
        
        content = file_result["content"]
        prompt = f"Analyze this file ({path}):\n\n```\n{content}\n```\n\n"
        if question:
            prompt += f"Specifically answer: {question}"
        else:
            prompt += "Provide a summary and key insights about this code/content."
        
        return self.chat(prompt)


ai_terminal = AITerminal()
