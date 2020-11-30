# Lint as: python3
# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Standarize logging for all errors."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os
import sys
from typing import Any, Optional

from glazier.lib import buildinfo
from glazier.lib import constants
from glazier.lib import logs

_SUFFIX = (f'Need help? Visit {constants.HELP_URI}')

build_info = buildinfo.BuildInfo()


def get_message(code: int, **kwargs) -> str:
  """Return dict value of a given error code.

  Args:
    code: Error code to return message for.
    **kwargs: Key/value pairs used in string.format() replacements in the error
      message.

  Returns:
    Message associated to the error code.

  Raises:
    GlazierError: Failed to determine error message from code
  """
  # TODO: Investigate how to gaurentee unique error codes
  errors: dict[int, str] = {
      4000: 'Uncaught exception',
      4301: 'Failed to determine error message from code',
      4302: 'Failed to collect logs',
      5000: 'Failed to reach web server',
      5300: 'Service unavailable',
  }

  error_msg = errors.get(code)

  if not error_msg:
    raise GlazierError(4301)

  # Enable passing variables to the errors dict by optionally inserting values
  # associated with the keyword arguments via string.format().
  return str(error_msg.format(*kwargs.values()))


def _collect():
  """Collect failure logs into a zip file."""
  try:
    logs.Collect(
        os.path.join(build_info.CachePath() + os.sep, 'glazier_logs.zip'))
  except logs.LogError as e:
    raise GlazierError(4302, exception=e, collect=False)


class GlazierError(Exception):
  """Custom exception class for Glazier errors."""

  def __init__(self,
               code: int = 4000,
               msg: Optional[str] = None,
               exception: Optional[Any] = None,
               collect: bool = True,
               **kwargs):
    """Log a terminating failure.

    Args:
      code: Error code to append to the failure message.
      msg: Error message that accompanies the failure.
      exception: Exception message string.
      collect: Whether to collect log files.
      **kwargs: Key/value pairs of any number of string replacements in the
      error message.
    """
    super(GlazierError, self).__init__()

    if not msg:
      msg = get_message(code, **kwargs)
    msg += '\n\n'

    # TODO: Add exception file and lineno.
    if exception:
      msg += f'Exception: {exception}\n\n'

    msg += f'{_SUFFIX}#{code}'

    if collect:
      _collect()

    logging.critical(msg)
    sys.exit(1)  # Necessary to avoid traceback
