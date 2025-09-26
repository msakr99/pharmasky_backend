from rest_framework.renderers import BaseRenderer
from django.template.loader import render_to_string
from tempfile import TemporaryFile
from django.utils.translation import deactivate
import logging

try:
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
    HTML = None
    FontConfiguration = None

logger = logging.getLogger("weasyprint")
try:
    logger.addHandler(logging.FileHandler("/var/log/medico/weasyprint.log"))
except:
    pass  # Skip logging setup if directory doesn't exist


class PDFRenderer(BaseRenderer):
    media_type = "application/pdf"
    format = "pdf"

    def get_template(self, view):
        template_name = getattr(view, "template_name", None)

        if isinstance(template_name, str):
            return template_name

        if template_name is None:
            template_name_fn = getattr(view, "get_template_name", None)

            if template_name_fn is not None:
                template_name = template_name_fn()

        assert template_name is not None, "missing template_name on view"

        return template_name

    def get_context_data(self, view, request):
        ctx = getattr(view, "template_context", None)

        if isinstance(ctx, dict):
            return ctx

        if ctx is None:
            ctx_fn = getattr(view, "get_template_context", None)

            if ctx_fn is not None:
                ctx = ctx_fn(request)

        assert ctx is not None, "missing template_context on view"

        return ctx

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not WEASYPRINT_AVAILABLE:
            # Return a simple error message as PDF content
            return b"PDF generation not available on this system. WeasyPrint dependencies missing."
        
        request = renderer_context.get("request")
        view = renderer_context.get("view")

        template_name = self.get_template(view)
        context = self.get_context_data(view, request)

        context.update({"data": data})

        font_config = FontConfiguration()
        html = render_to_string(template_name=template_name, context=context, request=request).encode(encoding="UTF-8")
        deactivate()
        document = HTML(string=html, base_url=request.build_absolute_uri()).render(font_config=font_config)

        return self._save_virtual_pdf(document)

    def _save_virtual_pdf(self, document: HTML):
        with TemporaryFile() as tmp:
            document.write_pdf(tmp, optimize_images=False)
            tmp.seek(0)
            virtual_pdf = tmp.read()
        return virtual_pdf
