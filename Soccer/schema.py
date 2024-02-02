from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from collections import OrderedDict
from drf_yasg import openapi


class OrderedSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        ordered_paths = OrderedDict()

        # Define the order of your endpoints here
        endpoint_order = [
            'signup',
            'login',
            'logout',
            'list_users',
            'user_details',
            'user_update',
            'team_update',
            'player_update',
            'delete_user',
            'transfer_list',
            'market_list',
            'buy_player',
        ]

        for endpoint in endpoint_order:
            for path, path_obj in schema.paths.items():
                if endpoint in path:
                    ordered_paths[path] = path_obj

        schema.paths = ordered_paths

        return schema

schema_view = get_schema_view(
   openapi.Info(
      title="Soccer App API",
      default_version='v1',
      description=
                """
                This is a simple Django REST Framework based api for \
                Soccer Online Game App where users can create there fantasy \
                Soccer teams and buy players from other teams.
                """
   ),
   public=True,
   generator_class=OrderedSchemaGenerator,
)
