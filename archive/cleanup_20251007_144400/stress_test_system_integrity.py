#!/usr/bin/env python3
"""
🚨 SYSTEM INTEGRITY STRESS TEST
Tests memory leaks, file handles, database connections, thread safety, exception handling
"""

import asyncio
import gc
import os
import psutil
import sqlite3
import threading
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import random
import tempfile
import shutil

class SystemIntegrityStressTest:
    def __init__(self):
        self.test_results = {}
        self.memory_baseline = None
        self.file_handle_baseline = None
        self.thread_count_baseline = None
        self.start_time = datetime.now()
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stress_test_system_integrity.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def get_file_handle_count(self):
        """Get current file handle count"""
        try:
            process = psutil.Process()
            return process.num_fds() if hasattr(process, 'num_fds') else len(process.open_files())
        except:
            return 0
    
    def get_thread_count(self):
        """Get current thread count"""
        try:
            process = psutil.Process()
            return process.num_threads()
        except:
            return threading.active_count()
    
    def test_memory_leak_detection(self, duration_hours: float = 24):
        """Test for memory leaks over extended period"""
        self.logger.info(f"🧠 Starting memory leak detection test for {duration_hours} hours")
        
        self.memory_baseline = self.get_memory_usage()
        memory_samples = []
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        while datetime.now() < end_time:
            # Simulate normal system operations
            await self._simulate_system_operations()
            
            current_memory = self.get_memory_usage()
            memory_samples.append({
                'timestamp': datetime.now(),
                'memory_mb': current_memory,
                'memory_growth': current_memory - self.memory_baseline
            })
            
            # Check for significant memory growth
            if current_memory - self.memory_baseline > 100:  # 100MB threshold
                self.logger.error(f"🚨 MEMORY LEAK DETECTED: {current_memory - self.memory_baseline:.2f}MB growth")
                self.test_results['memory_leak'] = {
                    'status': 'FAILED',
                    'growth_mb': current_memory - self.memory_baseline,
                    'threshold_mb': 100
                }
                return False
            
            await asyncio.sleep(300)  # Check every 5 minutes
        
        # Analyze memory trend
        if len(memory_samples) > 10:
            recent_avg = sum(s['memory_mb'] for s in memory_samples[-10:]) / 10
            early_avg = sum(s['memory_mb'] for s in memory_samples[:10]) / 10
            trend = recent_avg - early_avg
            
            if trend > 50:  # 50MB trend threshold
                self.logger.warning(f"⚠️ Memory trend detected: {trend:.2f}MB growth over time")
                self.test_results['memory_leak'] = {
                    'status': 'WARNING',
                    'trend_mb': trend,
                    'threshold_mb': 50
                }
            else:
                self.test_results['memory_leak'] = {'status': 'PASSED', 'trend_mb': trend}
        
        self.logger.info("✅ Memory leak detection test completed")
        return True
    
    async def _simulate_system_operations(self):
        """Simulate normal system operations to test memory usage"""
        # Create and destroy objects
        data = [random.random() for _ in range(10000)]
        processed = [x * 2 for x in data]
        del data, processed
        
        # Simulate file operations
        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write(b'stress test data' * 1000)
        
        # Force garbage collection
        gc.collect()
    
    def test_file_handle_exhaustion(self):
        """Test file handle exhaustion scenarios"""
        self.logger.info("📁 Testing file handle exhaustion")
        
        self.file_handle_baseline = self.get_file_handle_count()
        max_handles = 1000
        opened_files = []
        
        try:
            # Open many files rapidly
            for i in range(max_handles):
                try:
                    f = open(f'temp_stress_file_{i}.tmp', 'w')
                    opened_files.append(f)
                    
                    if len(opened_files) % 100 == 0:
                        current_handles = self.get_file_handle_count()
                        if current_handles > self.file_handle_baseline + 500:
                            self.logger.warning(f"⚠️ High file handle usage: {current_handles}")
                
                except OSError as e:
                    if "Too many open files" in str(e):
                        self.logger.error(f"🚨 File handle exhaustion at {len(opened_files)} files")
                        self.test_results['file_handles'] = {
                            'status': 'FAILED',
                            'max_files': len(opened_files),
                            'error': str(e)
                        }
                        break
            
            # Clean up
            for f in opened_files:
                try:
                    f.close()
                    os.remove(f.name)
                except:
                    pass
            
            if 'file_handles' not in self.test_results:
                self.test_results['file_handles'] = {
                    'status': 'PASSED',
                    'max_files': len(opened_files)
                }
        
        except Exception as e:
            self.logger.error(f"❌ File handle test failed: {e}")
            self.test_results['file_handles'] = {'status': 'ERROR', 'error': str(e)}
        
        self.logger.info("✅ File handle exhaustion test completed")
    
    def test_database_connection_limits(self):
        """Test database connection limits and cleanup"""
        self.logger.info("🗄️ Testing database connection limits")
        
        max_connections = 100
        connections = []
        
        try:
            # Create many database connections
            for i in range(max_connections):
                try:
                    conn = sqlite3.connect(':memory:')
                    conn.execute('CREATE TABLE test (id INTEGER, data TEXT)')
                    connections.append(conn)
                    
                except sqlite3.Error as e:
                    self.logger.error(f"🚨 Database connection limit reached at {len(connections)} connections")
                    self.test_results['database_connections'] = {
                        'status': 'FAILED',
                        'max_connections': len(connections),
                        'error': str(e)
                    }
                    break
            
            # Test concurrent operations
            def db_operation(conn):
                try:
                    conn.execute('INSERT INTO test (id, data) VALUES (?, ?)', (random.randint(1, 1000), 'stress_test'))
                    conn.commit()
                    result = conn.execute('SELECT COUNT(*) FROM test').fetchone()
                    return result[0] if result else 0
                except Exception as e:
                    self.logger.error(f"❌ Database operation failed: {e}")
                    return 0
            
            # Run concurrent operations
            threads = []
            for conn in connections[:10]:  # Test with 10 connections
                thread = threading.Thread(target=db_operation, args=(conn,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Clean up connections
            for conn in connections:
                try:
                    conn.close()
                except:
                    pass
            
            if 'database_connections' not in self.test_results:
                self.test_results['database_connections'] = {
                    'status': 'PASSED',
                    'max_connections': len(connections)
                }
        
        except Exception as e:
            self.logger.error(f"❌ Database connection test failed: {e}")
            self.test_results['database_connections'] = {'status': 'ERROR', 'error': str(e)}
        
        self.logger.info("✅ Database connection limits test completed")
    
    def test_thread_safety(self):
        """Test thread safety with concurrent access"""
        self.logger.info("🧵 Testing thread safety")
        
        self.thread_count_baseline = self.get_thread_count()
        shared_data = {'counter': 0, 'errors': []}
        lock = threading.Lock()
        
        def thread_worker(worker_id):
            try:
                for _ in range(1000):
                    with lock:
                        shared_data['counter'] += 1
                        # Simulate some processing
                        temp = shared_data['counter'] * 2
                        del temp
                    
                    # Small delay to increase chance of race conditions
                    time.sleep(0.001)
            
            except Exception as e:
                with lock:
                    shared_data['errors'].append(f"Worker {worker_id}: {str(e)}")
        
        # Create multiple threads
        threads = []
        num_threads = 20
        
        for i in range(num_threads):
            thread = threading.Thread(target=thread_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        expected_counter = num_threads * 1000
        actual_counter = shared_data['counter']
        
        if actual_counter != expected_counter:
            self.logger.error(f"🚨 Thread safety violation: Expected {expected_counter}, got {actual_counter}")
            self.test_results['thread_safety'] = {
                'status': 'FAILED',
                'expected': expected_counter,
                'actual': actual_counter,
                'errors': shared_data['errors']
            }
        else:
            self.test_results['thread_safety'] = {
                'status': 'PASSED',
                'final_counter': actual_counter,
                'errors': shared_data['errors']
            }
        
        self.logger.info("✅ Thread safety test completed")
    
    def test_exception_handling(self):
        """Test exception handling under various error conditions"""
        self.logger.info("⚠️ Testing exception handling")
        
        error_scenarios = [
            ('ZeroDivisionError', lambda: 1 / 0),
            ('ValueError', lambda: int('invalid')),
            ('TypeError', lambda: 'string' + 123),
            ('KeyError', lambda: {}['missing_key']),
            ('IndexError', lambda: [][0]),
            ('FileNotFoundError', lambda: open('nonexistent_file.txt')),
            ('PermissionError', lambda: open('/root/forbidden.txt', 'w')),
            ('MemoryError', self._trigger_memory_error),
            ('OSError', lambda: os.chmod('nonexistent', 0o777)),
            ('RuntimeError', lambda: exec('raise RuntimeError("Test error")'))
        ]
        
        handled_errors = 0
        unhandled_errors = []
        
        for error_name, error_func in error_scenarios:
            try:
                error_func()
                unhandled_errors.append(f"{error_name}: No exception raised")
            except Exception as e:
                handled_errors += 1
                # Test that we can handle and log the error properly
                try:
                    self.logger.info(f"✅ Handled {error_name}: {str(e)}")
                except:
                    unhandled_errors.append(f"{error_name}: Logging failed")
        
        if unhandled_errors:
            self.logger.error(f"🚨 Unhandled error scenarios: {unhandled_errors}")
            self.test_results['exception_handling'] = {
                'status': 'FAILED',
                'handled': handled_errors,
                'unhandled': unhandled_errors
            }
        else:
            self.test_results['exception_handling'] = {
                'status': 'PASSED',
                'handled': handled_errors
            }
        
        self.logger.info("✅ Exception handling test completed")
    
    def _trigger_memory_error(self):
        """Try to trigger a memory error"""
        try:
            # Try to allocate a very large amount of memory
            huge_list = [0] * (10**8)  # 100 million integers
            del huge_list
        except MemoryError:
            raise
    
    def test_resource_cleanup(self):
        """Test that all resources are properly cleaned up"""
        self.logger.info("🧹 Testing resource cleanup")
        
        initial_memory = self.get_memory_usage()
        initial_handles = self.get_file_handle_count()
        initial_threads = self.get_thread_count()
        
        # Create various resources
        resources = []
        
        # File resources
        for i in range(100):
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(b'stress test data' * 100)
            resources.append(('file', f.name))
            f.close()
        
        # Database connections
        for i in range(50):
            conn = sqlite3.connect(':memory:')
            conn.execute('CREATE TABLE test (id INTEGER)')
            resources.append(('database', conn))
        
        # Thread resources
        def dummy_thread():
            time.sleep(1)
        
        for i in range(20):
            thread = threading.Thread(target=dummy_thread)
            thread.start()
            resources.append(('thread', thread))
        
        # Wait for threads to complete
        for resource_type, resource in resources:
            if resource_type == 'thread':
                resource.join()
        
        # Clean up resources
        for resource_type, resource in resources:
            try:
                if resource_type == 'file':
                    os.remove(resource)
                elif resource_type == 'database':
                    resource.close()
                # Threads are already joined
            except Exception as e:
                self.logger.warning(f"⚠️ Cleanup warning for {resource_type}: {e}")
        
        # Force garbage collection
        gc.collect()
        
        # Check resource cleanup
        final_memory = self.get_memory_usage()
        final_handles = self.get_file_handle_count()
        final_threads = self.get_thread_count()
        
        memory_cleanup = final_memory - initial_memory < 10  # Less than 10MB difference
        handle_cleanup = final_handles <= initial_handles + 5  # Allow small increase
        thread_cleanup = final_threads <= initial_threads + 2  # Allow small increase
        
        if memory_cleanup and handle_cleanup and thread_cleanup:
            self.test_results['resource_cleanup'] = {
                'status': 'PASSED',
                'memory_diff': final_memory - initial_memory,
                'handle_diff': final_handles - initial_handles,
                'thread_diff': final_threads - initial_threads
            }
        else:
            self.test_results['resource_cleanup'] = {
                'status': 'FAILED',
                'memory_cleanup': memory_cleanup,
                'handle_cleanup': handle_cleanup,
                'thread_cleanup': thread_cleanup,
                'memory_diff': final_memory - initial_memory,
                'handle_diff': final_handles - initial_handles,
                'thread_diff': final_threads - initial_threads
            }
        
        self.logger.info("✅ Resource cleanup test completed")
    
    async def run_all_tests(self, duration_hours: float = 0.5):
        """Run all system integrity tests"""
        self.logger.info("🚀 Starting System Integrity Stress Tests")
        self.logger.info("=" * 60)
        
        # Run tests
        await self.test_memory_leak_detection(duration_hours)
        self.test_file_handle_exhaustion()
        self.test_database_connection_limits()
        self.test_thread_safety()
        self.test_exception_handling()
        self.test_resource_cleanup()
        
        # Generate report
        self._generate_report()
        
        return self.test_results
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        self.logger.info("📊 SYSTEM INTEGRITY STRESS TEST REPORT")
        self.logger.info("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result.get('status') == 'PASSED')
        failed = sum(1 for result in self.test_results.values() if result.get('status') == 'FAILED')
        warnings = sum(1 for result in self.test_results.values() if result.get('status') == 'WARNING')
        
        self.logger.info(f"✅ Passed: {passed}")
        self.logger.info(f"❌ Failed: {failed}")
        self.logger.info(f"⚠️ Warnings: {warnings}")
        
        for test_name, result in self.test_results.items():
            status = result.get('status', 'UNKNOWN')
            self.logger.info(f"{test_name.upper()}: {status}")
            if result.get('status') != 'PASSED':
                for key, value in result.items():
                    if key != 'status':
                        self.logger.info(f"  {key}: {value}")
        
        self.logger.info("=" * 60)
        self.logger.info(f"Total test duration: {datetime.now() - self.start_time}")

if __name__ == "__main__":
    async def main():
        tester = SystemIntegrityStressTest()
        await tester.run_all_tests(duration_hours=0.5)  # 30-minute test
    
    asyncio.run(main())
