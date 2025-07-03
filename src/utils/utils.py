"""
Utility functions and classes for Python 2 application.
Demonstrates various Python 2 patterns and idioms.
"""

import base64
import datetime
import hashlib
import logging
import os
import threading

import cPickle as pickle
import thread
from Queue import Empty, Queue


class Logger:
    """Custom logger class with Python 2 patterns."""

    def __init__(self, name, level="INFO"):
        self.name = name
        self.level = getattr(logging, level.upper())

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)

        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(formatter)

        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def debug(self, message):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message):
        """Log critical message."""
        self.logger.critical(message)


class FileHandler:
    """File handling utilities with Python 2 patterns."""

    def __init__(self):
        self.logger = Logger("file_handler")

    def read_file(self, filepath, encoding="utf-8"):
        """Read file content with encoding handling."""
        try:
            with open(filepath, "rb") as f:
                content = f.read()

            # Try to decode with specified encoding
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                # Fallback to utf-8 with error handling
                return content.decode("utf-8", "replace")

        except OSError as e:
            self.logger.error("Failed to read file %s: %s" % (filepath, str(e)))
            return None

    def write_file(self, filepath, content, encoding="utf-8"):
        """Write content to file with encoding."""
        try:
            if isinstance(content, unicode):
                content = content.encode(encoding)
            elif isinstance(content, str):
                # Assume it's already encoded
                pass
            else:
                content = str(content).encode(encoding)

            with open(filepath, "wb") as f:
                f.write(content)

            return True

        except (OSError, UnicodeEncodeError) as e:
            self.logger.error("Failed to write file %s: %s" % (filepath, str(e)))
            return False

    def append_to_file(self, filepath, content, encoding="utf-8"):
        """Append content to file."""
        try:
            if isinstance(content, unicode):
                content = content.encode(encoding)
            elif isinstance(content, str):
                pass
            else:
                content = str(content).encode(encoding)

            with open(filepath, "ab") as f:
                f.write(content)

            return True

        except (OSError, UnicodeEncodeError) as e:
            self.logger.error("Failed to append to file %s: %s" % (filepath, str(e)))
            return False

    def copy_file(self, source, destination):
        """Copy file from source to destination."""
        try:
            with open(source, "rb") as src:
                with open(destination, "wb") as dst:
                    while True:
                        chunk = src.read(8192)
                        if not chunk:
                            break
                        dst.write(chunk)

            return True

        except OSError as e:
            self.logger.error("Failed to copy file %s to %s: %s" % (source, destination, str(e)))
            return False

    def get_file_info(self, filepath):
        """Get file information."""
        try:
            stat = os.stat(filepath)
            return {
                "size": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime),
                "created": datetime.datetime.fromtimestamp(stat.st_ctime),
                "is_file": os.path.isfile(filepath),
                "is_dir": os.path.isdir(filepath),
                "permissions": oct(stat.st_mode)[-3:],
            }
        except OSError as e:
            self.logger.error("Failed to get file info for %s: %s" % (filepath, str(e)))
            return None

    def list_files(self, directory, pattern=None, recursive=False):
        """List files in directory with optional pattern matching."""
        import fnmatch

        files = []
        try:
            if recursive:
                for root, dirs, filenames in os.walk(directory):
                    for filename in filenames:
                        if pattern is None or fnmatch.fnmatch(filename, pattern):
                            files.append(os.path.join(root, filename))
            else:
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath):
                        if pattern is None or fnmatch.fnmatch(filename, pattern):
                            files.append(filepath)

        except OSError as e:
            self.logger.error("Failed to list files in %s: %s" % (directory, str(e)))

        return files


class CacheManager:
    """Simple cache manager using pickle for persistence."""

    def __init__(self, cache_dir="cache", max_size=1000):
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
        self.logger = Logger("cache")

        # Create cache directory
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        # Load existing cache
        self._load_cache()

    def _get_cache_file(self, key):
        """Get cache file path for key."""
        # Create safe filename from key
        safe_key = hashlib.md5(str(key)).hexdigest()
        return os.path.join(self.cache_dir, "%s.cache" % safe_key)

    def _load_cache(self):
        """Load cache from disk."""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith(".cache")]

            for cache_file in cache_files:
                filepath = os.path.join(self.cache_dir, cache_file)
                try:
                    with open(filepath, "rb") as f:
                        data = pickle.load(f)
                        if isinstance(data, dict) and "key" in data and "value" in data:
                            self.cache[data["key"]] = data["value"]
                            self.access_times[data["key"]] = data.get(
                                "access_time", datetime.datetime.now()
                            )
                except (OSError, pickle.PickleError):
                    # Remove corrupted cache file
                    os.remove(filepath)

        except OSError:
            pass  # Cache directory doesn't exist or is empty

    def get(self, key, default=None):
        """Get value from cache."""
        if key in self.cache:
            self.access_times[key] = datetime.datetime.now()
            return self.cache[key]
        return default

    def set(self, key, value, ttl=None):
        """Set value in cache."""
        # Check cache size and evict if necessary
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = value
        self.access_times[key] = datetime.datetime.now()

        # Save to disk
        self._save_to_disk(key, value)

    def _save_to_disk(self, key, value):
        """Save cache entry to disk."""
        try:
            cache_file = self._get_cache_file(key)
            data = {"key": key, "value": value, "access_time": self.access_times[key]}

            with open(cache_file, "wb") as f:
                pickle.dump(data, f)

        except (OSError, pickle.PickleError) as e:
            self.logger.warning("Failed to save cache entry: %s" % str(e))

    def _evict_oldest(self):
        """Evict oldest cache entry."""
        if not self.access_times:
            return

        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.delete(oldest_key)

    def delete(self, key):
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]

            # Remove from disk
            cache_file = self._get_cache_file(key)
            try:
                os.remove(cache_file)
            except OSError:
                pass

    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.access_times.clear()

        # Remove all cache files
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith(".cache")]
            for cache_file in cache_files:
                os.remove(os.path.join(self.cache_dir, cache_file))
        except OSError:
            pass


class ThreadPool:
    """Simple thread pool implementation for Python 2."""

    def __init__(self, num_threads=5):
        self.num_threads = num_threads
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.threads = []
        self.shutdown = False
        self.logger = Logger("threadpool")

        # Start worker threads
        for i in xrange(num_threads):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

    def _worker(self):
        """Worker thread function."""
        while not self.shutdown:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:  # Shutdown signal
                    break

                func, args, kwargs, task_id = task
                try:
                    result = func(*args, **kwargs)
                    self.result_queue.put((task_id, "success", result))
                except Exception as e:
                    self.result_queue.put((task_id, "error", str(e)))
                finally:
                    self.task_queue.task_done()

            except Empty:
                continue

    def submit(self, func, *args, **kwargs):
        """Submit a task to the thread pool."""
        task_id = thread.get_ident()  # Use thread ID as task ID
        task = (func, args, kwargs, task_id)
        self.task_queue.put(task)
        return task_id

    def get_result(self, timeout=None):
        """Get a result from the result queue."""
        try:
            return self.result_queue.get(timeout=timeout)
        except Empty:
            return None

    def wait_for_completion(self):
        """Wait for all tasks to complete."""
        self.task_queue.join()

    def shutdown_pool(self):
        """Shutdown the thread pool."""
        self.shutdown = True

        # Send shutdown signals
        for _ in xrange(self.num_threads):
            self.task_queue.put(None)

        # Wait for threads to finish
        for t in self.threads:
            t.join()


def encode_base64(data):
    """Encode data to base64 string."""
    if isinstance(data, unicode):
        data = data.encode("utf-8")
    return base64.b64encode(data)


def decode_base64(encoded_data):
    """Decode base64 string to data."""
    return base64.b64decode(encoded_data)


def calculate_md5(data):
    """Calculate MD5 hash of data."""
    if isinstance(data, unicode):
        data = data.encode("utf-8")
    return hashlib.md5(data).hexdigest()


def safe_unicode(obj, encoding="utf-8"):
    """Safely convert object to unicode."""
    if isinstance(obj, unicode):
        return obj
    elif isinstance(obj, str):
        return obj.decode(encoding, "replace")
    else:
        return unicode(str(obj), encoding, "replace")


def safe_str(obj, encoding="utf-8"):
    """Safely convert object to str."""
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, unicode):
        return obj.encode(encoding, "replace")
    else:
        return str(obj)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in xrange(0, len(lst), n):
        yield lst[i : i + n]


def flatten_dict(d, parent_key="", sep="_"):
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
