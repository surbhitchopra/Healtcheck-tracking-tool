"""
Script Helper for 1830PSS Health Check Integration
================================================

This module provides improved integration with the main script,
handling Windows-specific path issues and better error handling.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = BASE_DIR / "Script"
SCRIPT_INPUT_DIR = SCRIPT_DIR / "input-hc-report"
SCRIPT_OUTPUT_DIR = SCRIPT_DIR / "output"


class ScriptExecutor:
    """Handles execution of the main.py script with proper error handling"""
    
    def __init__(self):
        self.script_dir = SCRIPT_DIR
        self.main_script = SCRIPT_DIR / "main.py"
        self.python_exe = self._get_python_executable()
        
    def _get_python_executable(self):
        """Get the correct Python executable path"""
        # Try virtual environment first
        if sys.platform == "win32":
            venv_python = SCRIPT_DIR / "venv" / "Scripts" / "python.exe"
        else:
            venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
        
        if venv_python.exists():
            logger.info(f"Using virtual environment Python: {venv_python}")
            return venv_python
        
        # Fallback to system Python
        logger.warning(f"Virtual environment Python not found, using system Python: {sys.executable}")
        return Path(sys.executable)
    
    def validate_environment(self):
        """Validate that all required files and directories exist"""
        checks = {
            'script_dir': self.script_dir.exists(),
            'main_script': self.main_script.exists(),
            'python_exe': self.python_exe.exists(),
            'input_dir': SCRIPT_INPUT_DIR.exists(),
            'output_dir': SCRIPT_OUTPUT_DIR.exists(),
            'hcfuncs': (SCRIPT_DIR / "hcfuncs.py").exists(),
            'requirements': (SCRIPT_DIR / "requirements.txt").exists()
        }
        
        logger.info(f"Environment validation: {checks}")
        
        # Check if critical files are missing
        critical_missing = []
        if not checks['script_dir']:
            critical_missing.append("Script directory")
        if not checks['main_script']:
            critical_missing.append("main.py")
        if not checks['python_exe']:
            critical_missing.append("Python executable")
        if not checks['hcfuncs']:
            critical_missing.append("hcfuncs.py")
        
        if critical_missing:
            raise FileNotFoundError(f"Critical files missing: {', '.join(critical_missing)}")
        
        # Create missing directories
        if not checks['input_dir']:
            SCRIPT_INPUT_DIR.mkdir(exist_ok=True)
            logger.info(f"Created input directory: {SCRIPT_INPUT_DIR}")
        
        if not checks['output_dir']:
            SCRIPT_OUTPUT_DIR.mkdir(exist_ok=True)
            logger.info(f"Created output directory: {SCRIPT_OUTPUT_DIR}")
        
        return checks
    
    def validate_network_files(self, network_name):
        """Validate that network-specific files exist"""
        required_files = [
            f"{network_name}_HC_Issues_Tracker.xlsx",
            f"{network_name}_ignored_test_cases.txt",
            f"{network_name}_ignored_test_cases.xlsx"
        ]
        
        missing_files = []
        for filename in required_files:
            file_path = SCRIPT_DIR / filename
            if not file_path.exists():
                missing_files.append(filename)
        
        if missing_files:
            raise FileNotFoundError(f"Network setup files missing for {network_name}: {', '.join(missing_files)}")
        
        logger.info(f"All network files exist for: {network_name}")
        return True
    
    def check_input_files(self):
        """Check what files are in the input directory"""
        input_files = list(SCRIPT_INPUT_DIR.glob("*"))
        logger.info(f"Input files found: {[f.name for f in input_files]}")
        
        if len(input_files) == 0:
            raise FileNotFoundError("No input files found. Please upload HC report and inventory CSV.")
        
        # Check for required file types
        xlsx_files = [f for f in input_files if f.suffix.lower() == '.xlsx']
        csv_files = [f for f in input_files if f.suffix.lower() == '.csv']
        
        if len(xlsx_files) == 0:
            raise FileNotFoundError("No Excel (.xlsx) file found in input directory")
        
        if len(csv_files) == 0:
            raise FileNotFoundError("No CSV file found in input directory")
        
        return {
            'total_files': len(input_files),
            'xlsx_files': [f.name for f in xlsx_files],
            'csv_files': [f.name for f in csv_files]
        }
    
    def execute_script(self, timeout=7200):  # 2 hour timeout for large networks
        """Execute the main.py script with proper error handling"""
        try:
            # Validate environment before execution
            self.validate_environment()
            
            # Log execution details
            logger.info(f"Executing script: {self.main_script}")
            logger.info(f"Using Python: {self.python_exe}")
            logger.info(f"Working directory: {self.script_dir}")
            
            # Prepare command
            cmd = [str(self.python_exe), str(self.main_script)]
            
            # Execute script
            result = subprocess.run(
                cmd,
                cwd=str(self.script_dir),  # Very important: set working directory
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy()  # Use current environment
            )
            
            # Log results
            logger.info(f"Script exit code: {result.returncode}")
            if result.stdout:
                logger.info(f"Script stdout: {result.stdout[:500]}...")  # First 500 chars
            if result.stderr:
                logger.warning(f"Script stderr: {result.stderr[:500]}...")  # First 500 chars
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'error': result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Script execution timed out after {timeout} seconds"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'timeout': True
            }
        
        except FileNotFoundError as e:
            error_msg = f"File not found error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'file_error': True
            }
        
        except Exception as e:
            error_msg = f"Unexpected error during script execution: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'unexpected_error': True
            }
    
    def find_output_files(self):
        """Find generated output files"""
        output_files = []
        
        if SCRIPT_OUTPUT_DIR.exists():
            for file_path in SCRIPT_OUTPUT_DIR.glob("*"):
                if file_path.is_file():
                    output_files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'modified': file_path.stat().st_mtime
                    })
        
        logger.info(f"Output files found: {[f['name'] for f in output_files]}")
        return output_files
    
    def find_tracker_file(self):
        """Find the main HC Issues Tracker file in output"""
        output_files = self.find_output_files()
        
        for file_info in output_files:
            if "HC_Issues_Tracker" in file_info['name']:
                logger.info(f"Found tracker file: {file_info['name']}")
                return file_info
        
        logger.warning("No HC Issues Tracker file found in output")
        return None


def execute_health_check_script(network_name=None):
    """
    Main function to execute the health check script
    
    Args:
        network_name: Name of the network (for validation)
    
    Returns:
        dict: Execution result with success status and details
    """
    executor = ScriptExecutor()
    
    try:
        # Validate network setup if network name provided
        if network_name:
            executor.validate_network_files(network_name)
        
        # Check input files
        input_info = executor.check_input_files()
        logger.info(f"Input validation passed: {input_info}")
        
        # Execute the script
        result = executor.execute_script()
        
        # Find output files
        if result['success']:
            output_files = executor.find_output_files()
            tracker_file = executor.find_tracker_file()
            
            result.update({
                'output_files': output_files,
                'tracker_file': tracker_file,
                'input_info': input_info
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error in execute_health_check_script: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'validation_error': True
        }


# Helper function for testing
def test_script_integration():
    """Test the script integration without executing"""
    executor = ScriptExecutor()
    
    try:
        # Basic validation
        checks = executor.validate_environment()
        print(f"Environment checks: {checks}")
        
        # Check if we can find Python
        print(f"Python executable: {executor.python_exe}")
        print(f"Python exists: {executor.python_exe.exists()}")
        
        # Check script files
        print(f"Main script: {executor.main_script}")
        print(f"Main script exists: {executor.main_script.exists()}")
        
        # Check directories
        print(f"Input directory: {SCRIPT_INPUT_DIR}")
        print(f"Input directory exists: {SCRIPT_INPUT_DIR.exists()}")
        print(f"Output directory: {SCRIPT_OUTPUT_DIR}")
        print(f"Output directory exists: {SCRIPT_OUTPUT_DIR.exists()}")
        
        # List input files
        if SCRIPT_INPUT_DIR.exists():
            input_files = list(SCRIPT_INPUT_DIR.glob("*"))
            print(f"Input files: {[f.name for f in input_files]}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run test when executed directly
    test_script_integration()
