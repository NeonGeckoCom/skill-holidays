# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import requests
from ovos_utils.log import LOG
from ovos_workshop.skills.common_query_skill import CommonQuerySkill


class HolidaySkill(CommonQuerySkill):
    def __init__(self):
        super(HolidaySkill, self).__init__(name="HolidaySkill")
        self.holidays = {}

    @property
    def nager_url(self):
        """
        Get the base URL to use for holiday lookups.
        """
        return self.settings.get('url') or "https://date.nager.at/api/v3"

    @property
    def default_locale(self):
        """
        Get the default locale to use from a user's profile (if available) or
        global configuration.
        """
        return self.location.get('city',
                                 {}).get('state',
                                         {}).get('country',
                                                 {}).get('code') or "US"

    def _update_holidays(self, locale: str):
        """
        Update holidays for the configured locale. Cached on local filesystem
        for future references.
        """
        locale = locale or self.default_locale

        url = f"{self.nager_url}/NextPublicHolidays/{locale}"
        resp = requests.get(url)
        if resp.ok:
            holidays = resp.json()
            LOG.debug(holidays)
            self.holidays[locale] = holidays
        # TODO: Cache

    def holidays_by_date(self, locale: str) -> dict:
        """
        Get a dict of holidays, indexed by date 'YYYY-MM-DD'
        :param locale: locale to query holidays for
        :return: dict of holidays by date
        """
        locale = locale or self.default_locale
        if locale not in self.holidays:
            LOG.info(f"Updating holidays for: {locale}")
            self._update_holidays(locale)

        return {holiday['date']: holiday for holiday in self.holidays[locale]}

    def holidays_by_name(self, locale: str) -> dict:
        """
        Get a dict of holidays, indexed by name
        :param locale: locale to query holidays for
        :return: dict of holidays by name
        """
        return {holiday['name'].lower(): holiday
                for holiday in self.holidays[locale]}

    def CQS_match_query_phrase(self, phrase):
        pass


def create_skill():
    return HolidaySkill()
