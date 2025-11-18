"""Analysis engine modules"""
__all__ = ['InteractiveDCF']

try:
	from .interactive_dcf import InteractiveDCF  # noqa: F401
except Exception:
	# Keep the package import-safe even if optional dependencies for the
	# placeholder module are not available in test environments.
	pass
