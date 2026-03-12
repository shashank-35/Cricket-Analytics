"""Tests for utils/components.py — HTML component helpers."""

from utils.components import empty_state, form_badge, stat_row, tile, tile_grid


class TestTile:
    def test_basic_output(self) -> None:
        html = tile("Runs", 500)
        assert "Runs" in html
        assert "500" in html

    def test_escapes_html(self) -> None:
        html = tile("<script>alert(1)</script>", "val")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_delta(self) -> None:
        html = tile("X", 1, delta="+5%", delta_dir="up")
        assert "+5%" in html
        assert 'class="delta up"' in html
        assert "▲" in html


class TestTileGrid:
    def test_wraps_in_grid(self) -> None:
        html = tile_grid([tile("A", 1), tile("B", 2)])
        assert 'class="tile-grid"' in html


class TestStatRow:
    def test_basic(self) -> None:
        html = stat_row("Country", "India")
        assert "Country" in html
        assert "India" in html

    def test_escapes(self) -> None:
        html = stat_row("<b>bold</b>", "val")
        assert "<b>" not in html


class TestFormBadge:
    def test_good(self) -> None:
        html = form_badge("Good")
        assert "badge-good" in html
        assert "●" in html
        assert 'aria-label' in html

    def test_escapes(self) -> None:
        html = form_badge("<img src=x>")
        assert "&lt;img" in html
        assert 'class="badge-poor"' in html  # unknown form defaults to 'poor'


class TestEmptyState:
    def test_basic(self) -> None:
        html = empty_state("🔍", "No Results", "Try a different search.")
        assert 'class="empty-state"' in html
        assert "No Results" in html
        assert "Try a different search." in html

    def test_escapes(self) -> None:
        html = empty_state("<script>", "<b>Title</b>", "<p>Desc</p>")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert "&lt;b&gt;" in html
