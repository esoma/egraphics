from __future__ import annotations

# egraphics
from .test_texture import TextureTest

# egraphics
from egraphics import Texture2d


class TestTexture2d(TextureTest):
    size_length = 2
    wrap_length = 2

    @classmethod
    def create_texture(
        cls,
        size,
        components,
        data_type,
        buffer,
        *,
        anisotropy=None,
        mipmap_selection=None,
        minify_filter=None,
        magnify_filter=None,
        wrap=None,
        wrap_color=None,
    ) -> Texture2d:
        return Texture2d(
            size,
            components,
            data_type,
            buffer,
            anisotropy=anisotropy,
            mipmap_selection=mipmap_selection,
            minify_filter=minify_filter,
            magnify_filter=magnify_filter,
            wrap=wrap,
            wrap_color=wrap_color,
        )
