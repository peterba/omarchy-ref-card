TEX := tectonic
PDFTOPPM ?= pdftoppm
PDFINFO ?= pdfinfo
FFMPEG ?= ffmpeg
PYTHON ?= python3
UPSTREAM_DIR ?=
SOURCE := omarchy-reference-card.tex
LETTER_SOURCE := omarchy-reference-card-letter.tex
A4_SOURCE := omarchy-reference-card-a4.tex
OUTPUT_DIR := build
LETTER_PDF := $(OUTPUT_DIR)/omarchy-reference-card-letter.pdf
A4_PDF := $(OUTPUT_DIR)/omarchy-reference-card-a4.pdf
PDFS := $(LETTER_PDF) $(A4_PDF)
PERSONALIZATION := $(wildcard personalize.tex)
COMMON_SOURCES := Makefile $(SOURCE) omarchy-card.sty defaults/bindings.tex assets/omarchy-wordmark.png $(PERSONALIZATION)
CHECK_DIR := $(OUTPUT_DIR)/check
LETTER_CHECK_LOG := $(CHECK_DIR)/omarchy-reference-card-letter.log
A4_CHECK_LOG := $(CHECK_DIR)/omarchy-reference-card-a4.log
RENDER_DIR := $(OUTPUT_DIR)/render
PREVIEW_DIR := docs/images
PREVIEW := $(PREVIEW_DIR)/omarchy-reference-card-preview.png
SKILL_SOURCE := $(CURDIR)/codex-skill/omarchy-ref-card
CODEX_SKILLS_DIR ?= $(HOME)/.codex/skills
SKILL_TARGET := $(CODEX_SKILLS_DIR)/omarchy-ref-card

.PHONY: all letter a4 personalize list-bindings check test check-upstream check-upstream-reconcile update-upstream-lock render preview install-skill clean

all: $(PDFS)

letter: $(LETTER_PDF)

a4: $(A4_PDF)

$(LETTER_PDF): $(LETTER_SOURCE) $(COMMON_SOURCES)
	mkdir -p $(OUTPUT_DIR)
	$(TEX) --synctex --outdir $(OUTPUT_DIR) $(LETTER_SOURCE)

$(A4_PDF): $(A4_SOURCE) $(COMMON_SOURCES)
	mkdir -p $(OUTPUT_DIR)
	$(TEX) --synctex --outdir $(OUTPUT_DIR) $(A4_SOURCE)

personalize:
	@test -e personalize.tex || cp personalize.example.tex personalize.tex

list-bindings:
	@awk -F '[{}]' '/^\\DeclareBinding/ { print $$2 }' defaults/bindings.tex

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -v

check-upstream: test
	@test -n "$(UPSTREAM_DIR)" || { echo "Set UPSTREAM_DIR to an Omarchy checkout."; exit 2; }
	$(PYTHON) -B scripts/audit_upstream.py --upstream "$(UPSTREAM_DIR)" --require-commit

check-upstream-reconcile: test
	@test -n "$(UPSTREAM_DIR)" || { echo "Set UPSTREAM_DIR to an Omarchy checkout."; exit 2; }
	$(PYTHON) -B scripts/audit_upstream.py --upstream "$(UPSTREAM_DIR)" --skip-lock

update-upstream-lock: test
	@test -n "$(UPSTREAM_DIR)" || { echo "Set UPSTREAM_DIR to an Omarchy checkout."; exit 2; }
	$(PYTHON) -B scripts/audit_upstream.py --upstream "$(UPSTREAM_DIR)" --write-lock

check: $(PDFS)
	mkdir -p $(CHECK_DIR)
	$(TEX) --keep-logs --outdir $(CHECK_DIR) $(LETTER_SOURCE)
	$(TEX) --keep-logs --outdir $(CHECK_DIR) $(A4_SOURCE)
	@! grep -E 'Overfull \\[hv]box|LaTeX Error|Package .* Error' $(LETTER_CHECK_LOG) $(A4_CHECK_LOG)
	@grep -Eq 'Output written on .*\(2 pages,' $(LETTER_CHECK_LOG)
	@grep -Eq 'Output written on .*\(2 pages,' $(A4_CHECK_LOG)
	@$(PDFINFO) $(CHECK_DIR)/omarchy-reference-card-letter.pdf | grep -Eq 'Page size: +792 x 612 pts \(letter\)'
	@$(PDFINFO) $(CHECK_DIR)/omarchy-reference-card-a4.pdf | grep -Eq 'Page size: +841\.89 x 595\.28 pts \(A4\)'
	@echo "TeX checks passed for Letter and A4: two pages each and no errors or overfull boxes."

render: $(PDFS)
	mkdir -p $(RENDER_DIR)
	$(PDFTOPPM) -png -r 150 $(LETTER_PDF) $(RENDER_DIR)/omarchy-reference-card-letter
	$(PDFTOPPM) -png -r 150 $(A4_PDF) $(RENDER_DIR)/omarchy-reference-card-a4
	@echo "Rendered pages are in $(RENDER_DIR)."

preview: render
	mkdir -p $(PREVIEW_DIR)
	$(FFMPEG) -hide_banner -loglevel error -y \
	  -i $(RENDER_DIR)/omarchy-reference-card-letter-1.png \
	  -i $(RENDER_DIR)/omarchy-reference-card-letter-2.png \
	  -filter_complex "[0:v]scale=692:-1[left];[1:v]scale=692:-1[right];[left][right]xstack=inputs=2:layout=0_0|708_0:fill=white,format=rgb24" \
	  -frames:v 1 $(PREVIEW)
	@echo "Updated README preview: $(PREVIEW)"

install-skill:
	mkdir -p "$(CODEX_SKILLS_DIR)"
	@test ! -e "$(SKILL_TARGET)" && test ! -L "$(SKILL_TARGET)" || \
	  { echo "Refusing to replace existing $(SKILL_TARGET)"; exit 1; }
	ln -s "$(SKILL_SOURCE)" "$(SKILL_TARGET)"
	@echo "Installed skill: $(SKILL_TARGET) -> $(SKILL_SOURCE)"

clean:
	rm -rf $(OUTPUT_DIR)
