#!/usr/bin/env python3.5
#
# Copyright (c) 2013-2016 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

# To run this program, the file ``ssh_host_key`` must exist with an SSH
# private key in it to use as a server host key. An SSH host certificate
# can optionally be provided in the file ``ssh_host_key-cert.pub``.
#
# The file ``ssh_user_ca`` must exist with a cert-authority entry of
# the certificate authority which can sign valid client certificates.

import asyncio, asyncssh, sys

async def handle_session(stdin, stdout, stderr):
    term_type = stdout.channel.get_terminal_type()
    width, height, pixwidth, pixheight = stdout.channel.get_terminal_size()

    stdout.write('Terminal type: %s, size: %sx%s' % (term_type, width, height))
    if pixwidth and pixheight:
        stdout.write(' (%sx%s pixels)' % (pixwidth, pixheight))
    stdout.write('\nTry resizing your window!\n')

    while not stdin.at_eof():
        try:
            await stdin.read()
        except asyncssh.TerminalSizeChanged as exc:
            stdout.write('New window size: %sx%s' % (exc.width, exc.height))
            if exc.pixwidth and exc.pixheight:
                stdout.write(' (%sx%s pixels)' % (exc.pixwidth, exc.pixheight))
            stdout.write('\n')

async def start_server():
    await asyncssh.listen('', 8022, server_host_keys=['ssh_host_key'],
                          authorized_client_keys='ssh_user_ca',
                          session_factory=handle_session)

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()
