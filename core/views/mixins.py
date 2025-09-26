from django.utils.encoding import escape_uri_path
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from accounts.models import User


class PDFFileMixin(object):
    filename = "export.pdf"

    def get_filename(self, request=None, *args, **kwargs):
        """
        Returns a custom filename for the pdf.
        """
        return self.filename

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Return the response with the proper content disposition and the customized
        filename instead of the browser default (or lack thereof).
        """
        response = super().finalize_response(request, response, *args, **kwargs)
        if isinstance(response, Response) and response.accepted_renderer.format == "pdf":
            response["content-disposition"] = "attachment; filename={}".format(
                self.get_filename(request=request, *args, **kwargs),
            )
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response


class RoleViewMixin(object):
    filter_role_use_pk = False
    role_filter = None
    additional_role_filter = None

    def _get_filter_field(self, user):
        try:
            user_role = self._get_user_role(user)
            return self.role_filter[user_role]
        except KeyError:
            raise PermissionDenied(_("You don't have permission to perform this action."))

    def _get_additional_filter_fields(self, user) -> dict | None:
        if self.additional_role_filter is None:
            return None

        try:
            user_role = self._get_user_role(user)
            return self.additional_role_filter[user_role]
        except KeyError:
            return None

    def _filter_queryset(self, user, queryset, filter_field, additional_filter_kwargs):
        if filter_field is not None:
            filter_kwargs = {filter_field: user.pk if self.filter_role_use_pk else user}
            queryset = queryset.filter(**filter_kwargs)

        if additional_filter_kwargs is not None:
            queryset = queryset.filter(**additional_filter_kwargs)

        return queryset

    def _get_user(self) -> User:
        try:
            request = getattr(self, "request")
            return request.user
        except Exception as e:
            raise e

    def _get_user_role(self, user: User) -> str:
        if not user.is_authenticated:
            raise PermissionDenied(_("You don't have permission to perform this action."))

        try:
            role = getattr(user, "role")
            return role
        except Exception as e:
            raise e

    def filter_role(self, queryset):
        if self.role_filter is None:
            return queryset

        user = self._get_user()
        filter_field = self._get_filter_field(user)
        additional_filter_kwargs = self._get_additional_filter_fields(user)
        return self._filter_queryset(user, queryset, filter_field, additional_filter_kwargs)
