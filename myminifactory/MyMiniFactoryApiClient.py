# Copyright (c) 2018 Chris ter Beke.
# Thingiverse plugin is released under the terms of the LGPLv3 or higher.
from typing import List, Callable, Any, Union, Dict, Tuple, Optional, cast

from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from UM.Logger import Logger
from cura.CuraApplication import CuraApplication

from ..Settings import Settings
from ..api.APIClient import ApiClient
from ..api.JSONObject import JSONObject
from ..api.Models import Thing

class MyMiniFactoryApiClient(ApiClient):
    """ Client for interacting with the MyMiniFactory API. """

    # API constants.
    @property
    def _root_url(self):
        return "https://www.myminifactory.com/api/v2"

    @property
    def _auth(self):
        return None

    @property
    def user_id(self):
        return CuraApplication.getInstance().getPreferences().getValue(Settings.MYMINIFACTORY_USER_NAME_PREFERENCES_KEY)

    def getUserCollectionsUrl(self) -> str:
        return "users/{}/collections".format(self.user_id)

    def getCollectionUrl(self, collection_id: int) -> str:
        return "collections/{}".format(collection_id)

    def getLikesUrl(self) -> str:
        return "users/{}/objects_liked".format(self.user_id)

    def getUserThingsUrl(self) -> str:
        return "users/{}/objects".format(self.user_id)

    def getUserMakesUrl(self) -> str:
        return None

    def getThing(self, thing_id: int, on_finished: Callable[[JSONObject], Any],
                 on_failed: Optional[Callable[[JSONObject], Any]] = None) -> None:
        """
        Get a single thing by ID.
        :param thing_id: The thing ID.
        :param on_finished: Callback method to receive the async result on.
        :param on_failed: Callback method to receive failed request on.
        """
        url = "{}/objects/{}".format(self._root_url, thing_id)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, on_failed)

    def getThingFiles(self, thing_id: int, on_finished: Callable[[List[JSONObject]], Any],
                      on_failed: Optional[Callable[[JSONObject], Any]] = None) -> None:
        """
        Get a thing's files by ID.
        :param thing_id: The thing ID.
        :param on_finished: Callback method to receive the async result on.
        :param on_failed: Callback method to receive failed request on.
        """
        url = "{}/object/{}/files".format(self._root_url, thing_id)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, on_failed)

    def downloadThingFile(self, file_id: int, on_finished: Callable[[bytes], Any]) -> None:
        """
        Download a thing file by its ID.
        :param file_id: The file ID to download.
        :param on_finished: Callback method to receive the async result on as bytes.
        """
        url = "{}/download/{}/?downloadfile={}.stl".format(self._root_url, file_id, file_id)
        reply = self._manager.get(self._createEmptyRequest(url))

        # We use a custom parse function for this API call because the response is not a JSON model.
        def parse() -> None:
            result = bytes(reply.readAll())
            self._anti_gc_callbacks.remove(parse)
            on_finished_cast = cast(Callable[[bytes], Any], on_finished)
            on_finished_cast(result)

        self._anti_gc_callbacks.append(parse)
        reply.finished.connect(parse)

    def get(self, query: str, page: int, on_finished: Callable[[List[JSONObject]], Any],
            on_failed: Optional[Callable[[JSONObject], Any]] = None) -> None:
        """
        Get things by query.
        :param query: The things to get.
        :param page: Page number of query results (for pagination).
        :param on_finished: Callback method to receive the async result on.
        :param on_failed: Callback method to receive failed request on.
        """
        url = "{}/{}?per_page={}&page={}&key={}".format(self._root_url, query, Settings.MYMINIFACTORY_API_PER_PAGE, page, Settings.MYMINIFACTORY_API_TOKEN)
        reply = self._manager.get(self._createEmptyRequest(url))
        self._addCallback(reply, on_finished, on_failed)

    @staticmethod
    def convertJsonToThing(data: Union[JSONObject, List[JSONObject]]) -> Thing:
        return Thing({
            'URL': data.public_url if hasattr(data, 'public_url') else None,
            'ID': data.id if hasattr(data, 'id') else None,
            'NAME': data.name if hasattr(data, 'name') else None,
            'DESCRIPTION': data.description if hasattr(data, 'description') else None,
            'THUMBNAIL': data.thumbnail if hasattr(data, 'thumbnail') else None
        })
