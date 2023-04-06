# -*- coding:utf-8 -*-
#
# Copyright 2023 © AE UTBM
# ae@utbm.fr / ae.info@utbm.fr
# All contributors are listed in the CONTRIBUTORS file.
#
# This file is part of the website of the UTBM Student Association (AE UTBM),
# https://ae.utbm.fr.
#
# You can find the whole source code at https://github.com/ae-utbm/sith3
#
# LICENSED UNDER THE GNU GENERAL PUBLIC LICENSE VERSION 3 (GPLv3)
# SEE : https://raw.githubusercontent.com/ae-utbm/sith3/master/LICENSE
# OR WITHIN THE LOCAL FILE "LICENSE"
#
# PREVIOUSLY LICENSED UNDER THE MIT LICENSE,
# SEE : https://raw.githubusercontent.com/ae-utbm/sith3/master/LICENSE.old
# OR WITHIN THE LOCAL FILE "LICENSE.old"
#

from django.core.management.base import BaseCommand
from django.db import connection

from galaxy.models import Galaxy

import logging


class Command(BaseCommand):
    help = (
        "Rule the Galaxy! "
        "Reset the whole galaxy and compute once again all the relation scores of all users. "
        "As the sith's users are rather numerous, this command might be quite expensive in memory "
        "and CPU time. Please keep this fact in mind when scheduling calls to this command in a production "
        "environment."
    )

    def handle(self, *args, **options):
        logger = logging.getLogger("main")
        if options["verbosity"] > 1:
            logger.setLevel(logging.DEBUG)
        elif options["verbosity"] > 0:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.NOTSET)

        logger.info("The Galaxy is being ruled by the Sith.")
        Galaxy.rule()
        logger.info(
            "Caching current Galaxy state for a quicker display of the Empire's power."
        )
        Galaxy.make_state()

        logger.info("Ruled the galaxy in {} queries.".format(len(connection.queries)))
        if options["verbosity"] > 2:
            for q in connection.queries:
                logger.debug(q)
