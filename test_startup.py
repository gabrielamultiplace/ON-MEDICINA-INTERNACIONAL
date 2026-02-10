#!/usr/bin/env python
"""Test app startup directly."""

import sys
import logging

# Set up logging before importing app
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting app test...")

try:
    from app import app, init_db, seed_admin
    logger.info("✓ App imported successfully")
    
    logger.info("Initializing database...")
    init_db()
    logger.info("✓ Database initialized")
    
    logger.info("Seeding admin...")
    seed_admin()
    logger.info("✓ Admin user seeded")
    
    logger.info("Starting Flask development server...")
    logger.info(f"App has {len(app.blueprints)} blueprints")
    for name, bp in app.blueprints.items():
        logger.info(f"  - {name}: {bp.url_prefix}")
    
    # Don't use reloader to see errors
    logger.info("Running on http://0.0.0.0:5000")
    app.run(
        debug=True,  # Enable debug mode to see errors
        use_reloader=False,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
    
except Exception as e:
    logger.exception("Fatal error during startup:")
    sys.exit(1)
