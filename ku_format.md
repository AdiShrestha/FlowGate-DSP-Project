# KU DoCSE Project Report — LaTeX Format Specification

**Purpose:** This document instructs any AI chatbot to produce a correctly formatted LaTeX/Overleaf project report that exactly matches the official Department of Computer Science and Engineering (DoCSE), Kathmandu University submission template. Every rule below is derived directly from the official Word template (XML-level analysis). Follow all specifications without deviation unless the user explicitly overrides a value.

---

## 0. How to Use This File

When asked to write a project report, the AI must:
1. Read **all sections** of this document first.
2. Generate a **complete, compilable `.tex` file** (or multiple files if the project is large).
3. Populate all content sections with project-specific content provided by the user.
4. Never omit any structural element (front matter pages, TOC, list of figures, etc.) unless the user explicitly says it is not needed.
5. Ensure the document compiles on **Overleaf** (Latexmk, pdfLaTeX engine assumed unless user specifies otherwise).

---

## 1. Paper and Margins

| Property          | Value             | LaTeX equivalent             |
|-------------------|-------------------|------------------------------|
| Paper size        | US Letter (8.5" × 11") | `letterpaper` in geometry |
| Left margin       | 1.50 inches       | `left=1.5in`                 |
| Right margin      | 1.25 inches       | `right=1.25in`               |
| Top margin        | 1.25 inches       | `top=1.25in`                 |
| Bottom margin     | 1.25 inches       | `bottom=1.25in`              |
| Header distance from top edge | 0.5 inches | `headheight=0.5in, headsep=0pt` |
| Footer distance from bottom edge | 0.5 inches | `footskip=0.5in`          |
| Text width (computed) | 5.75 inches  | —                            |

---

## 2. Typography

| Property              | Value              | Notes                                         |
|-----------------------|--------------------|-----------------------------------------------|
| Body font family      | Times New Roman    | Use `newtxtext` + `newtxmath` in LaTeX        |
| Body font size        | 12pt               | Set as document class option                  |
| Body text alignment   | Fully justified    | LaTeX default; do **not** use `\raggedright`  |
| First-line indent     | 0pt (none)         | `\setlength{\parindent}{0pt}`                 |
| Line spacing          | 1.5×               | `\setstretch{1.5}` from `setspace` package    |
| Paragraph spacing (after) | 18pt          | `\setlength{\parskip}{18pt}`                  |

### Heading sizes (all bold, Times New Roman)

| Level                      | LaTeX command       | Size   | Notes                                            |
|----------------------------|---------------------|--------|--------------------------------------------------|
| Chapter (e.g., Chapter 1)  | `\chapter{}`        | 16pt   | Format: "Chapter N⟨tab⟩Title" — see §6          |
| Section (e.g., 1.1)        | `\section{}`        | 14pt   | Numbered X.Y, bold                               |
| Subsection (e.g., 1.1.1)   | `\subsection{}`     | 13pt   | Numbered X.Y.Z, bold                             |
| Subsubsection (1.1.1.1)    | `\subsubsection{}`  | 12pt   | Numbered X.Y.Z.W, bold (same size as body text)  |
| Unnumbered front-matter headings (Abstract, List of Figures, etc.) | `\chapter*{}` styled | 16pt bold | Added to TOC manually |

### Caption style

| Property    | Value                                        |
|-------------|----------------------------------------------|
| Font size   | 9pt bold                                     |
| Alignment   | Centered                                     |
| Table captions | **Above** the table, format: `Table X.Y Caption text` |
| Figure captions | **Below** the figure, format: `Figure X.Y Caption text` |

---

## 3. Page Numbering

| Section                  | Numeral style        | Starts at    |
|--------------------------|----------------------|--------------|
| Title page               | None (suppressed)    | —            |
| Bona fide Certificate    | None (suppressed)    | —            |
| Abstract                 | Lowercase Roman      | i            |
| Table of Contents        | Lowercase Roman      | continues    |
| List of Figures          | Lowercase Roman      | continues    |
| List of Tables           | Lowercase Roman      | continues    |
| Acronyms/Abbreviations   | Lowercase Roman      | continues    |
| Chapter 1 onwards        | Arabic               | 1            |
| References, Bibliography, Appendix | Arabic     | continues    |

Page numbers appear in the **footer, centered**. There is **no header** (no running title, no horizontal rule at the top).

---

## 4. Logo

The KU logo image file is named `ku_logo.png` and will be provided by the user in the same directory as the `.tex` file.

- Placement: Title page only, centered horizontally
- Size: `width=1.2in, height=1.2in` (approximately 1.22" × 1.21" from template XML; use `keepaspectratio`)
- Do NOT place the logo anywhere else in the document

---

## 5. Required LaTeX Packages and Full Preamble

Copy this preamble verbatim. Do not remove any package. Adjust only the content variables at the top.

```latex
\documentclass[12pt]{report}

%% ─── USER-CONFIGURABLE VARIABLES ────────────────────────────────────────────
\newcommand{\ProjectTitle}{Your Project Title Here}
\newcommand{\CourseCode}{COMP XXX}
\newcommand{\YearSemester}{Fourth Year / Eighth Semester}
\newcommand{\StudentOne}{Full Name (Roll No.)}
\newcommand{\StudentTwo}{Full Name (Roll No.)}
\newcommand{\StudentThree}{Full Name (Roll No.)}  % Remove line if only 2 students
\newcommand{\SupervisorName}{Dr. Supervisor Name}
\newcommand{\SupervisorDesignation}{Associate Professor}
\newcommand{\SupervisorDept}{Department of Computer Science and Engineering}
\newcommand{\SubmissionDate}{Month Year}
%% ─────────────────────────────────────────────────────────────────────────────

%% Fonts — Times New Roman equivalent (high quality, works on Overleaf)
\usepackage{newtxtext, newtxmath}

%% Page geometry — exact KU DoCSE margins
\usepackage[
  letterpaper,
  left=1.5in,
  right=1.25in,
  top=1.25in,
  bottom=1.25in,
  headheight=14pt,
  headsep=0pt,
  footskip=0.5in
]{geometry}

%% Line and paragraph spacing
\usepackage{setspace}
\setstretch{1.5}              % 1.5× line spacing throughout
\setlength{\parindent}{0pt}   % No first-line indent
\setlength{\parskip}{18pt}    % 18pt spacing between paragraphs

%% Headers and footers
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}                            % Clear all header/footer fields
\fancyfoot[C]{\thepage}              % Centered page number in footer only
\renewcommand{\headrulewidth}{0pt}    % No horizontal line in header
\renewcommand{\footrulewidth}{0pt}    % No horizontal line in footer

%% Plain style redefinition (used on chapter-opening pages)
\fancypagestyle{plain}{%
  \fancyhf{}
  \fancyfoot[C]{\thepage}
  \renewcommand{\headrulewidth}{0pt}
}

%% Heading formatting
\usepackage{titlesec}

% Chapter heading: "Chapter N    Title" — 16pt bold, no extra top padding
\titleformat{\chapter}[hang]
  {\fontsize{16pt}{19.2pt}\selectfont\bfseries\setstretch{1.0}}
  {Chapter~\thechapter}
  {1.5em}
  {}
\titlespacing*{\chapter}{0pt}{0pt}{18pt}

% Section: 14pt bold, numbered X.Y
\titleformat{\section}[hang]
  {\fontsize{14pt}{16.8pt}\selectfont\bfseries\setstretch{1.0}}
  {\thesection}
  {1em}
  {}
\titlespacing*{\section}{0pt}{18pt}{0pt}

% Subsection: 13pt bold, numbered X.Y.Z, indented
\titleformat{\subsection}[hang]
  {\fontsize{13pt}{15.6pt}\selectfont\bfseries\setstretch{1.0}}
  {\thesubsection}
  {1em}
  {}
\titlespacing*{\subsection}{1.5em}{10pt}{0pt}

% Subsubsection: 12pt bold, numbered X.Y.Z.W, further indented
\titleformat{\subsubsection}[hang]
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries\setstretch{1.0}}
  {\thesubsubsection}
  {1em}
  {}
\titlespacing*{\subsubsection}{3em}{10pt}{0pt}

%% Table of Contents formatting
\usepackage{titletoc}
\usepackage{tocloft}

% "Table of Contents" title centered and bold
\renewcommand{\cfttoctitlefont}{\hfill\fontsize{16pt}{19.2pt}\selectfont\bfseries}
\renewcommand{\cftaftertoctitle}{\hfill}
\setlength{\cftbeforetoctitleskip}{0pt}
\setlength{\cftaftertoctitleskip}{18pt}

% Chapter entries in TOC: "Chapter N    Title" with dotted leaders
\renewcommand{\cftchappresnum}{Chapter~}
\renewcommand{\cftchapaftersnum}{}
\setlength{\cftchapnumwidth}{6em}      % Width of "Chapter N" label
\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftchapfont}{}
\renewcommand{\cftchappagefont}{}

% Section entries indented
\setlength{\cftsecindent}{6em}
\setlength{\cftsecnumwidth}{2.5em}

% Subsection entries further indented
\setlength{\cftsubsecindent}{9em}
\setlength{\cftsubsecnumwidth}{3em}

% TOC depth: show up to subsubsections (level 3)
\setcounter{tocdepth}{3}
\setcounter{secnumdepth}{4}    % Number down to subsubsection level

%% List of Figures title formatting
\renewcommand{\cftloftitlefont}{\hfill\fontsize{16pt}{19.2pt}\selectfont\bfseries}
\renewcommand{\cftafterloftitle}{\hfill}

%% List of Tables title formatting
\renewcommand{\cftlottitlefont}{\hfill\fontsize{16pt}{19.2pt}\selectfont\bfseries}
\renewcommand{\cftafterlottitle}{\hfill}

%% Caption formatting: 9pt bold, centered; table above, figure below
\usepackage{caption}
\captionsetup{
  font={bf, footnotesize},   % bold, 9pt (footnotesize ~= 9pt at 12pt doc)
  labelsep=space,            % "Figure X.Y " with space before caption text
  justification=centering,
  singlelinecheck=false
}
\captionsetup[table]{position=above}   % Table captions go ABOVE the table
\captionsetup[figure]{position=below}  % Figure captions go BELOW the figure

%% Figure numbering: chapter.figure
\usepackage{chngcntr}
\counterwithin{figure}{chapter}
\counterwithin{table}{chapter}

%% Graphics
\usepackage{graphicx}

%% APA citations and references
\usepackage[style=apa, backend=biber]{biblatex}
\addbibresource{references.bib}

%% Miscellaneous utilities
\usepackage{microtype}        % Better text justification
\usepackage{enumitem}         % Control list spacing
\usepackage{booktabs}         % Professional table rules (optional but good)
\usepackage{array}            % Table column formatting
\usepackage{hyperref}         % Clickable TOC links (optional; comment out if unwanted)
\hypersetup{
  colorlinks=false,
  hidelinks
}
```

---

## 6. Chapter Heading Visual Format

The chapter heading must visually appear as:

```
Chapter 1        Introduction
```

- "Chapter N" and the chapter title are on **the same line**
- There is approximately **1.5em of horizontal space** between "Chapter N" and the title
- The heading is **left-aligned** (not centered)
- Font: 16pt bold Times New Roman
- **No** extra blank lines above the heading — the top margin alone provides the spacing
- **No** chapter number on its own line; both label and title are together

The `\chapter{Introduction}` command with the titlesec formatting above produces this automatically. Never write the chapter number manually.

**Unnumbered front-matter headings** (Abstract, List of Figures, etc.) use `\chapter*{}` but must appear in the TOC. Use `\addcontentsline{toc}{chapter}{Heading Name}` immediately after `\chapter*{}`.

Example:
```latex
\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}
```

---

## 7. Complete Document Structure

The document must follow this exact order. Do not reorder sections. Do not omit any section (use placeholder text if content is not yet available).

```
Title Page                   (no page number)
Bona fide Certificate        (no page number)
──── begin roman numerals ────
Abstract                     (page i)
Table of Contents            (page ii)
List of Figures              (page iii)
List of Tables               (page iv)
Acronyms/Abbreviations       (page v)
──── begin arabic numerals ────
Chapter 1: Introduction      (page 1)
  1.1 Background
  1.2 Objectives
  1.3 Motivation and Significance
Chapter 2: Related Works     (page 3)
Chapter 3: Design and Implementation  (page 4)
  3.1 System Requirement Specifications
    3.1.1 Software Specifications
    3.1.2 Hardware Specifications
Chapter 4: Discussion on the achievements  (page 6)
  4.1 Features
Chapter 5: Conclusion and Recommendation  (page 7)
  5.1 Limitations
  5.2 Future Enhancement
References                   (continues arabic)
Bibliography (Optional)      (continues arabic)
APPENDIX                     (continues arabic)
```

Chapter numbers, section numbers, and page numbers above are from the template and will differ in the actual report — they are shown here only to illustrate the required structure.

---

## 8. Title Page LaTeX Code

```latex
\begin{document}

%% ─── TITLE PAGE ─────────────────────────────────────────────────────────────
\begin{titlepage}
  \centering
  \setstretch{1.0}         % Single spacing on title page
  \setlength{\parskip}{0pt}

  {\fontsize{14pt}{16.8pt}\selectfont\bfseries Kathmandu University\par}
  {\fontsize{14pt}{16.8pt}\selectfont\bfseries Department of Computer Science and Engineering\par}
  {\fontsize{14pt}{16.8pt}\selectfont\bfseries Dhulikhel, Kavre\par}

  \vspace{1cm}

  \includegraphics[width=1.2in, height=1.2in, keepaspectratio]{ku_logo.png}

  \vspace{0.8cm}

  {\fontsize{12pt}{14.4pt}\selectfont\bfseries A Project Report\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries on\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries ``\ProjectTitle''\par}

  \vspace{0.5cm}

  {\fontsize{12pt}{14.4pt}\selectfont\bfseries [Code No: \CourseCode]\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries
    (For partial fulfillment of \YearSemester{} in Computer Science/Engineering)\par}

  \vspace{1.2cm}

  {\fontsize{12pt}{14.4pt}\selectfont\bfseries Submitted by\par}

  \vspace{0.3cm}

  {\fontsize{12pt}{14.4pt}\selectfont\bfseries \StudentOne\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries \StudentTwo\par}
  % Include the line below only if there is a third student:
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries \StudentThree\par}

  \vspace{1.2cm}

  {\fontsize{12pt}{14.4pt}\selectfont\bfseries Submitted to\par}

  \vspace{0.3cm}

  {\fontsize{12pt}{14.4pt}\selectfont\bfseries \SupervisorName\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries Department of Computer Science and Engineering\par}

  \vspace{1cm}

  {\fontsize{12pt}{14.4pt}\selectfont\bfseries Submission Date: \SubmissionDate\par}

\end{titlepage}
%% ─────────────────────────────────────────────────────────────────────────────
```

---

## 9. Bona Fide Certificate Page LaTeX Code

```latex
%% ─── BONA FIDE CERTIFICATE ──────────────────────────────────────────────────
\thispagestyle{empty}     % No page number
\setstretch{1.0}
\setlength{\parskip}{0pt}

\begin{center}
  {\fontsize{16pt}{19.2pt}\selectfont\bfseries Bona fide Certificate\par}
\end{center}

\vspace{3cm}

\begin{center}
  {\bfseries This project work on\par}
  \vspace{0.3cm}
  {\bfseries ``\ProjectTitle''\par}
  \vspace{0.3cm}
  {\bfseries is the bona fide work of\par}
  \vspace{0.3cm}
  {\bfseries ``\StudentOne, \StudentTwo''
    % Add \StudentThree if applicable
    \par}
  \vspace{0.3cm}
  {\bfseries who carried out the project work under my supervision.\par}
\end{center}

\vspace{4cm}

{\bfseries Project Supervisor\par}

\vspace{1.5cm}

{\bfseries \rule{6cm}{0.4pt}\par}

{\bfseries \SupervisorName\par}
{\bfseries \SupervisorDesignation\par}
{\bfseries \SupervisorDept\par}

\vspace{0.8cm}
{\bfseries Date:\par}

\newpage
\setstretch{1.5}
\setlength{\parskip}{18pt}
%% ─────────────────────────────────────────────────────────────────────────────
```

---

## 10. Front Matter (Roman Numerals) — LaTeX Code

After the certificate page, switch to Roman page numbering:

```latex
%% ─── BEGIN FRONT MATTER (roman page numbers) ────────────────────────────────
\pagenumbering{roman}
\pagestyle{fancy}
```

### Abstract

```latex
\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}

% 150–200 words covering: What did you do? Why? How?
% Structure: Background (1-2 sentences), Purpose/Aim (1-2 sentences),
% Procedure and Method/Tools (1-2 sentences), Expected Outcome (1-2 sentences),
% Conclusion (1 sentence), Recommendation (1 sentence)

[Abstract content here — 150 to 200 words]

\bigskip
\noindent\textbf{Keywords:} \textit{keyword1, keyword2, keyword3, keyword4}
```

### Table of Contents

```latex
\tableofcontents
\newpage
```

### List of Figures

```latex
\chapter*{List of Figures}
\addcontentsline{toc}{chapter}{List of Figures}
\listoffigures
\newpage
```

### List of Tables

```latex
\chapter*{List of Tables}
\addcontentsline{toc}{chapter}{List of Tables}
\listoftables
\newpage
```

### Acronyms / Abbreviations

Use a two-column tabular layout matching the template. The first column contains the abbreviation (bold-width), the second contains the expansion.

```latex
\chapter*{Acronyms/Abbreviations}
\addcontentsline{toc}{chapter}{Acronyms/Abbreviations}

\begin{tabbing}
  \hspace{3cm} \= \kill
  \textbf{ABC}  \> Long form of ABC \\
  \textbf{XYZ}  \> Long form of XYZ \\
  % Add all abbreviations used in the document
\end{tabbing}
\newpage
```

---

## 11. Main Matter (Arabic Numerals) — LaTeX Code

```latex
%% ─── BEGIN MAIN MATTER (arabic page numbers starting at 1) ──────────────────
\pagenumbering{arabic}
\setcounter{page}{1}
\pagestyle{fancy}
```

Then write chapters normally:

```latex
\chapter{Introduction}

[Brief introductory paragraph for the chapter]

\section{Background}

[2–3 paragraphs, 200–400 words. Cover recent developments in the field and
drawbacks/significance of existing work.]

\section{Objectives}

List project objectives (not exceeding 4) as a bullet list:

\begin{itemize}
  \item Objective one
  \item Objective two
  \item Objective three
\end{itemize}

\section{Motivation and Significance}

[Motivation paragraph and list answering: Why this topic? How does it address
existing drawbacks? How is it different from existing work?]

\begin{itemize}
  \item Why this topic was chosen
  \item How work addresses drawbacks of existing systems
  \item How it differs from existing works
\end{itemize}
```

---

## 12. Figures

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.8\textwidth]{figure_filename.png}
  \caption{Caption text describing the figure}
  \label{fig:label_name}
\end{figure}
```

- Caption appears **below** the figure automatically (configured in preamble)
- Reference in text: `Figure~\ref{fig:label_name}`
- Numbering: `Figure 3.1`, `Figure 3.2`, etc. (chapter.sequential)
- Do NOT add "Figure" manually in the caption text — the `\caption{}` command adds it automatically

---

## 13. Tables

```latex
\begin{table}[h]
  \caption{Caption text describing the table}
  \label{tab:label_name}
  \centering
  \begin{tabular}{|c|c|c|}
    \hline
    \textbf{Header} & \textbf{Header} & \textbf{Header} \\
    \hline
    Content & Content & Content \\
    \hline
  \end{tabular}
\end{table}
```

- Caption appears **above** the table automatically (configured in preamble)
- Numbering: `Table 3.1`, `Table 3.2`, etc. (chapter.sequential)
- Header row: bold text, centered
- All cells have borders (use `|c|c|c|` or similar with `\hline`)
- Do NOT add "Table" manually — `\caption{}` adds it automatically

---

## 14. In-Text Citations and References

This report uses **APA citation format** throughout.

### In-text citation patterns

```latex
% (Author, Year) — parenthetical
\parencite{bibtexkey}

% Author (Year) — narrative
\textcite{bibtexkey}

% Multiple authors (Author1 & Author2, Year)
\parencite{bibtexkey1, bibtexkey2}
```

APA in-text examples that appear in the template:
- `According to \textcite{john2012}, Management System should include...`
- `\textcite{thapa2010} have done similar project where...`
- `...has features like \parencite{rai2012}.`

### References section (end of document)

```latex
%% ─── REFERENCES ─────────────────────────────────────────────────────────────
\chapter*{References}
\addcontentsline{toc}{chapter}{References}
\printbibliography[heading=none]
```

### Sample `references.bib` entries (APA format)

```bibtex
@article{rai2012,
  author    = {Rai, B. and Parajuli, K.},
  year      = {2012},
  title     = {The Minesweepers},
  journal   = {Example Journal Name}
}

@techreport{taylor2008,
  author    = {Taylor, D. and Procter, M.},
  year      = {2008},
  title     = {The literature review: A few tips on conducting it},
  institution = {Health Sciences Writing Centre}
}
```

---

## 15. Bibliography (Optional)

```latex
%% ─── BIBLIOGRAPHY (Optional) ────────────────────────────────────────────────
\chapter*{Bibliography \textit{(Optional)}}
\addcontentsline{toc}{chapter}{Bibliography (Optional)}

[List books, internet sources, and similar works consulted indirectly during
the project. Use APA format. Present as a formatted list similar to References.]
```

---

## 16. Appendix

```latex
%% ─── APPENDIX ───────────────────────────────────────────────────────────────
\chapter*{APPENDIX}
\addcontentsline{toc}{chapter}{APPENDIX}

[Include supporting data, screenshots, code listings, etc.]
```

Note: The word "APPENDIX" is in **ALL CAPS** as shown in the template.

---

## 17. Section Content Requirements

These are the expected contents for each section per the KU template. The AI must fill these with accurate project-specific content.

### Chapter 1: Introduction

**1.1 Background**
- At least 2–3 paragraphs, 200–400 words
- Cover: recent development in the field, drawbacks and significance of existing works

**1.2 Objectives**
- Maximum 4 bullet points
- Each objective should be one specific, measurable goal

**1.3 Motivation and Significance**
- Why this topic was chosen
- How the work addresses drawbacks of existing systems
- How it differs from existing works
- Brief mention of key project features

### Chapter 2: Related Works

- Review of similar/earlier projects, papers, or systems
- Referencing in APA in-text format
- Include: comparison, strengths/weaknesses of existing works, relevance to the current project

### Chapter 3: Design and Implementation

- Detailed explanation of the development procedure
- Include: algorithms, flowcharts, system diagrams (Use Case, ER, Class, Activity, etc.)
- **3.1 System Requirement Specifications**
  - **3.1.1 Software Specifications** — functional and non-functional requirements, dependencies
  - **3.1.2 Hardware Specifications** — hardware requirements and minimum configuration

### Chapter 4: Discussion on the Achievements

- Challenges faced during development
- Deviations from objectives, negative findings
- Measurable results and comparisons
- **4.1 Features** — list and describe implemented features

### Chapter 5: Conclusion and Recommendation

- Summary of achieved/unachieved goals with reasoning
- Must not contradict the objectives stated in Chapter 1
- **5.1 Limitations** — current limitations of the work
- **5.2 Future Enhancement** — possible improvements or extensions

---

## 18. Complete Skeleton `.tex` File

Below is the complete document skeleton. The AI must fill in all `[...]` placeholders with real project content.

```latex
\documentclass[12pt]{report}

%% ─── PREAMBLE ───────────────────────────────────────────────────────────────
%% (Paste the full preamble from Section 5 here)

\newcommand{\ProjectTitle}{Your Project Title}
\newcommand{\CourseCode}{COMP XXX}
\newcommand{\YearSemester}{Fourth Year / Eighth Semester}
\newcommand{\StudentOne}{Name One (Roll No.)}
\newcommand{\StudentTwo}{Name Two (Roll No.)}
\newcommand{\StudentThree}{Name Three (Roll No.)}
\newcommand{\SupervisorName}{Dr. Supervisor Name}
\newcommand{\SupervisorDesignation}{Associate Professor}
\newcommand{\SupervisorDept}{Department of Computer Science and Engineering}
\newcommand{\SubmissionDate}{Month Year}

\usepackage{newtxtext, newtxmath}
\usepackage[letterpaper, left=1.5in, right=1.25in, top=1.25in, bottom=1.25in,
            headheight=14pt, headsep=0pt, footskip=0.5in]{geometry}
\usepackage{setspace}
\setstretch{1.5}
\setlength{\parindent}{0pt}
\setlength{\parskip}{18pt}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\thepage}\renewcommand{\headrulewidth}{0pt}}
\usepackage{titlesec}
\titleformat{\chapter}[hang]{\fontsize{16pt}{19.2pt}\selectfont\bfseries\setstretch{1.0}}{Chapter~\thechapter}{1.5em}{}
\titlespacing*{\chapter}{0pt}{0pt}{18pt}
\titleformat{\section}[hang]{\fontsize{14pt}{16.8pt}\selectfont\bfseries\setstretch{1.0}}{\thesection}{1em}{}
\titlespacing*{\section}{0pt}{18pt}{0pt}
\titleformat{\subsection}[hang]{\fontsize{13pt}{15.6pt}\selectfont\bfseries\setstretch{1.0}}{\thesubsection}{1em}{}
\titlespacing*{\subsection}{1.5em}{10pt}{0pt}
\titleformat{\subsubsection}[hang]{\fontsize{12pt}{14.4pt}\selectfont\bfseries\setstretch{1.0}}{\thesubsubsection}{1em}{}
\titlespacing*{\subsubsection}{3em}{10pt}{0pt}
\usepackage{tocloft}
\renewcommand{\cfttoctitlefont}{\hfill\fontsize{16pt}{19.2pt}\selectfont\bfseries}
\renewcommand{\cftaftertoctitle}{\hfill}
\setlength{\cftbeforetoctitleskip}{0pt}
\setlength{\cftaftertoctitleskip}{18pt}
\renewcommand{\cftchappresnum}{Chapter~}
\renewcommand{\cftchapaftersnum}{}
\setlength{\cftchapnumwidth}{6em}
\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}
\setlength{\cftsecindent}{6em}
\setlength{\cftsecnumwidth}{2.5em}
\setlength{\cftsubsecindent}{9em}
\setlength{\cftsubsecnumwidth}{3em}
\setcounter{tocdepth}{3}
\setcounter{secnumdepth}{4}
\renewcommand{\cftloftitlefont}{\hfill\fontsize{16pt}{19.2pt}\selectfont\bfseries}
\renewcommand{\cftafterloftitle}{\hfill}
\renewcommand{\cftlottitlefont}{\hfill\fontsize{16pt}{19.2pt}\selectfont\bfseries}
\renewcommand{\cftafterlottitle}{\hfill}
\usepackage{caption}
\captionsetup{font={bf,footnotesize}, labelsep=space, justification=centering, singlelinecheck=false}
\captionsetup[table]{position=above}
\captionsetup[figure]{position=below}
\usepackage{chngcntr}
\counterwithin{figure}{chapter}
\counterwithin{table}{chapter}
\usepackage{graphicx}
\usepackage[style=apa, backend=biber]{biblatex}
\addbibresource{references.bib}
\usepackage{microtype}
\usepackage{enumitem}
\usepackage{array}
\usepackage{hyperref}
\hypersetup{colorlinks=false, hidelinks}
%% ─────────────────────────────────────────────────────────────────────────────

\begin{document}

%% ─── TITLE PAGE ─────────────────────────────────────────────────────────────
\begin{titlepage}
  \centering
  \setstretch{1.0}
  \setlength{\parskip}{0pt}
  {\fontsize{14pt}{16.8pt}\selectfont\bfseries Kathmandu University\par}
  {\fontsize{14pt}{16.8pt}\selectfont\bfseries Department of Computer Science and Engineering\par}
  {\fontsize{14pt}{16.8pt}\selectfont\bfseries Dhulikhel, Kavre\par}
  \vspace{1cm}
  \includegraphics[width=1.2in, keepaspectratio]{ku_logo.png}
  \vspace{0.8cm}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries A Project Report\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries on\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries ``\ProjectTitle''\par}
  \vspace{0.5cm}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries [Code No: \CourseCode]\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries (For partial fulfillment of \YearSemester{} in Computer Science/Engineering)\par}
  \vspace{1.2cm}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries Submitted by\par}
  \vspace{0.3cm}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries \StudentOne\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries \StudentTwo\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries \StudentThree\par}
  \vspace{1.2cm}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries Submitted to\par}
  \vspace{0.3cm}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries \SupervisorName\par}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries Department of Computer Science and Engineering\par}
  \vspace{1cm}
  {\fontsize{12pt}{14.4pt}\selectfont\bfseries Submission Date: \SubmissionDate\par}
\end{titlepage}
%% ─────────────────────────────────────────────────────────────────────────────

%% ─── BONA FIDE CERTIFICATE ──────────────────────────────────────────────────
\thispagestyle{empty}
\setstretch{1.0}
\setlength{\parskip}{0pt}
\begin{center}
  {\fontsize{16pt}{19.2pt}\selectfont\bfseries Bona fide Certificate\par}
\end{center}
\vspace{3cm}
\begin{center}
  {\bfseries This project work on\par}
  \vspace{0.3cm}
  {\bfseries ``\ProjectTitle''\par}
  \vspace{0.3cm}
  {\bfseries is the bona fide work of\par}
  \vspace{0.3cm}
  {\bfseries ``\StudentOne, \StudentTwo, \StudentThree''\par}
  \vspace{0.3cm}
  {\bfseries who carried out the project work under my supervision.\par}
\end{center}
\vspace{4cm}
{\bfseries Project Supervisor\par}
\vspace{1.5cm}
{\bfseries \rule{6cm}{0.4pt}\par}
{\bfseries \SupervisorName\par}
{\bfseries \SupervisorDesignation\par}
{\bfseries \SupervisorDept\par}
\vspace{0.8cm}
{\bfseries Date:\par}
\newpage
\setstretch{1.5}
\setlength{\parskip}{18pt}
%% ─────────────────────────────────────────────────────────────────────────────

%% ─── FRONT MATTER ───────────────────────────────────────────────────────────
\pagenumbering{roman}

\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}

[Write 150–200 word abstract here covering: background, purpose/aim,
procedure and method/tools, expected outcome, conclusion, recommendation.]

\bigskip
\noindent\textbf{Keywords:} \textit{keyword1, keyword2, keyword3}

\tableofcontents
\newpage

\chapter*{List of Figures}
\addcontentsline{toc}{chapter}{List of Figures}
\listoffigures
\newpage

\chapter*{List of Tables}
\addcontentsline{toc}{chapter}{List of Tables}
\listoftables
\newpage

\chapter*{Acronyms/Abbreviations}
\addcontentsline{toc}{chapter}{Acronyms/Abbreviations}
\begin{tabbing}
  \hspace{3cm} \= \kill
  \textbf{XYZ}  \> Expanded Form of XYZ \\
  \textbf{ABC}  \> Expanded Form of ABC \\
\end{tabbing}
\newpage
%% ─────────────────────────────────────────────────────────────────────────────

%% ─── MAIN MATTER ─────────────────────────────────────────────────────────────
\pagenumbering{arabic}
\setcounter{page}{1}

\chapter{Introduction}

[Introductory paragraph for Chapter 1]

\section{Background}

[2–3 paragraphs, 200–400 words on recent developments and drawbacks of
existing work in the field]

\section{Objectives}

\begin{itemize}
  \item [Objective 1]
  \item [Objective 2]
  \item [Objective 3]
\end{itemize}

\section{Motivation and Significance}

[Motivation paragraph]

\begin{itemize}
  \item Why this topic was chosen
  \item How the work addresses existing drawbacks
  \item How it differs from existing works
\end{itemize}


\chapter{Related Works}

[Discussion of similar earlier projects, works, and papers in APA in-text
citation format. Discuss strengths, weaknesses, comparisons.]


\chapter{Design and Implementation}

[Overview paragraph describing the design approach]

\begin{table}[h]
  \caption{Sample Table Title}
  \label{tab:sample}
  \centering
  \begin{tabular}{|c|c|c|}
    \hline
    \textbf{Header} & \textbf{Header} & \textbf{Header} \\
    \hline
    Content & Content & Content \\
    \hline
  \end{tabular}
\end{table}

\section{System Requirement Specifications}

[Introductory paragraph]

\subsection{Software Specifications}

[Functional and non-functional requirements, software dependencies]

\begin{figure}[h]
  \centering
  \includegraphics[width=0.75\textwidth]{diagram.png}
  \caption{Sample Use Case Diagram}
  \label{fig:usecase}
\end{figure}

\subsection{Hardware Specifications}

[Hardware requirements and minimum system configuration]


\chapter{Discussion on the Achievements}

[Overview paragraph on challenges, deviations, and results]

\section{Features}

[List and brief description of implemented features]


\chapter{Conclusion and Recommendation}

[Summary of achieved and unachieved goals]

\section{Limitations}

[Limitations of the current implementation]

\section{Future Enhancement}

[Possible extensions and improvements]


%% ─── REFERENCES ─────────────────────────────────────────────────────────────
\chapter*{References}
\addcontentsline{toc}{chapter}{References}
\printbibliography[heading=none]

%% ─── BIBLIOGRAPHY (Optional) ────────────────────────────────────────────────
% Remove this section if not needed
\chapter*{Bibliography \textit{(Optional)}}
\addcontentsline{toc}{chapter}{Bibliography (Optional)}

[APA-format list of indirectly consulted sources]

%% ─── APPENDIX ───────────────────────────────────────────────────────────────
\chapter*{APPENDIX}
\addcontentsline{toc}{chapter}{APPENDIX}

[Supporting data, screenshots, code listings, raw outputs, etc.]

\end{document}
```

---

## 19. Critical Rules — What NOT To Do

The AI must never do any of the following:

1. **Do NOT use `a4paper`** — the template is US Letter (8.5" × 11")
2. **Do NOT center the chapter heading** — it is left-aligned with "Chapter N" label
3. **Do NOT write "Chapter N" manually in the chapter title argument** — the titlesec format adds it automatically. Write `\chapter{Introduction}`, not `\chapter{Chapter 1: Introduction}`
4. **Do NOT use the `\raggedright` command** — body text must be fully justified
5. **Do NOT add a horizontal header rule** — there is no header line in this template
6. **Do NOT put figure captions above figures** — they go below
7. **Do NOT put table captions below tables** — they go above
8. **Do NOT use `\indent` to create first-line indents** — paragraphs have no first-line indent
9. **Do NOT write "Figure" or "Table" manually** before `\caption{}` — it is added automatically
10. **Do NOT use `\maketitle`** — the title page is built manually with the `titlepage` environment
11. **Do NOT use `\chapter{Abstract}`** — use `\chapter*{Abstract}` + `\addcontentsline`
12. **Do NOT use `\appendix`** — the APPENDIX section is a plain `\chapter*{APPENDIX}`
13. **Do NOT change from `report` document class** — the KU template structure (chapters, sections) requires `report`
14. **Do NOT skip `\addcontentsline` after any `\chapter*{}`** — every front/back matter heading must appear in the TOC
15. **Do NOT use default LaTeX fonts (Computer Modern)** — use `newtxtext, newtxmath` for Times New Roman
16. **Do NOT set line spacing to single or double** — it is always 1.5×
17. **Do NOT use more than 4 bullet points for objectives** — the template specifies "not exceeding 4"

---

## 20. Overleaf Compilation Notes

- **Compiler:** Set to pdfLaTeX (default on Overleaf). If using `biblatex`, switch to "pdfLaTeX + Biber" in the Overleaf menu.
- **Bibliography:** Create `references.bib` as a separate file in the Overleaf project and add all sources there.
- **Images:** Upload `ku_logo.png` and all figure images directly to the Overleaf project root (same directory as `main.tex`).
- **Compile order for bibliography:** The project must be compiled at least twice after adding/changing citations for cross-references and citations to resolve.
- **If `newtxtext` is unavailable:** Fall back to `\usepackage{mathptmx}` for Times-compatible fonts.
- **If `biblatex` compilation fails:** Use `\usepackage{apacite}` with `\bibliographystyle{apacite}` and `\bibliography{references}` instead.

---

*End of KU DoCSE LaTeX Format Specification*
*Template analyzed: DoCSE_Semester_Report_Template_.docx (XML-level inspection)*
*Applicable for: Kathmandu University, Department of Computer Science and Engineering, all project submissions requiring this template format*
