all: report.pdf

report.pdf: report.tex
	pdflatex report
	bibtex report
	pdflatex report
	pdflatex report

scores:
	bash scores.sh report.aux ../data/quality-assessment/dare_assessment.csv >scores.tex

clean:
	rm -f *.aux *.bbl *.blg *.cut *.dvi *.log *.out *.synctex.gz *.fdb_latexmk *.fls *.toc *.nav *.snm *.vrb *.pdf

crop:
	for f in figures/*.pdf; do pdfcrop $$f $$f; done

