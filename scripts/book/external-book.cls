%% external-book.cls: the design of a textbook typeset from the site (build_book.py).
%%
%% The site is set as a LaTeX document would be (New Computer Modern Book, amsthm's
%% statements and proofs, enumerate's labels); this class is that design on paper.
%% Typeset with LuaLaTeX.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{external-book}[2026/11/15 Textbooks of the External site]
\LoadClass[11pt,twoside,openright]{book}

%% -- Page: 7 x 10 in, the trim of most mathematics textbooks; 30pc of text, 42 lines.
\RequirePackage[paperwidth=7in, paperheight=10in, textwidth=30pc, lines=42,
  inner=0.875in, top=0.95in, headsep=1.5pc, footskip=2.5pc]{geometry}

%% -- Faces: New Computer Modern Book for text and math, as on the site (style.scss,
%% MathJax's mathjax-newcm). amsmath goes before unicode-math.
\RequirePackage{amsmath}
\RequirePackage{mathtools}
\RequirePackage{newcomputermodern}
\RequirePackage[final]{microtype}
\input{site-macros}

\setlength{\parindent}{1em}
\setlength{\emergencystretch}{2em}
\frenchspacing
% No line of a paragraph alone at the foot or the head of a page; a line before a display
% may be, or a tall display (a Hasse diagram) would take its whole paragraph to the next
% page and leave the foot of this one empty.
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=1000
\raggedbottom
\allowdisplaybreaks[1]

%% -- Statements and proofs (amsthm). The head is printed as the label reads, number and
%% all: \begin{statement}{plain}{Theorem 3.1.8}[Steinitz replacement theorem]. `plain`
%% sets the body in italic, as the site sets a theorem, lemma, proposition or corollary
%% (math-statement-italic); `definition` sets it upright.
\RequirePackage{amsthm}
\newcommand*\ext@unithead{}
\theoremstyle{plain}
\newtheorem*{ext@plain}{\ext@unithead}
\theoremstyle{definition}
\newtheorem*{ext@definition}{\ext@unithead}
\NewDocumentEnvironment{statement}{m m o}
  {\def\ext@unithead{#2}\IfNoValueTF{#3}{\begin{ext@#1}}{\begin{ext@#1}[#3]}}
  {\end{ext@#1}}

\renewcommand\qedsymbol{\ensuremath{\square}}
% A proof the page ends without a QED.
\newcommand\noqed{\renewcommand\qedsymbol{}}
% A proof inside a proof, ended by a black square.
\NewDocumentEnvironment{subproof}{O{Subproof}}
  {\begin{proof}[#1]\renewcommand\qedsymbol{\ensuremath{\blacksquare}}}
  {\end{proof}}
% A QED outside any proof.
\newcommand\qedsymbolhere[1]{{\renewcommand\qedsymbol{\ensuremath{#1}}\qed}}
% A target for \hyperref, raised to the line it names.
\newcommand\unitlabel[1]{\phantomsection\label{#1}}

%% -- Lists, as post.css sets them after enumitem: labels 1em in from the text (flush
%% with the item text in a nested list), in a box as wide as the widest label, then 0.5em.
%% A label stays upright in an italic statement.
\RequirePackage{enumitem}
\setlist{topsep=.5\baselineskip, partopsep=0pt, itemsep=0pt, parsep=0pt,
  labelindent=1em, leftmargin=*, labelsep=.5em, align=left, font=\upshape}
\setlist[enumerate,1]{label=(\arabic*)}
\setlist[enumerate,2]{label=(\alph*), labelindent=0pt, topsep=0pt}
\setlist[enumerate,3]{label=(\roman*), labelindent=0pt, topsep=0pt}
\setlist[enumerate,4]{label=(\Alph*), labelindent=0pt, topsep=0pt}
\setlist[itemize,2]{labelindent=0pt, topsep=0pt}
\setlist[itemize,3]{labelindent=0pt, topsep=0pt}
\setlist[itemize,4]{labelindent=0pt, topsep=0pt}

%% -- Diagrams: tikz-cd and TikZ; the `hasse` style comes from the site (tikz-preamble.tex).
\RequirePackage{tikz-cd}

%% -- Figures: amsart's caption, numbered as its label reads.
\RequirePackage{caption}
\DeclareCaptionLabelFormat{ams}{\textsc{#1}~#2}
\DeclareCaptionLabelSeparator{ams}{.\enspace}
\captionsetup{labelformat=ams, labelsep=ams}
\newcommand\figurecaption[2]{\renewcommand\thefigure{#1}\caption{#2}}

%% -- Headings.
\RequirePackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\raggedright}
  {\large\scshape\textls[80]{chapter\enspace\thechapter}}
  {1.4pc}
  {\fontsize{26}{30}\selectfont}
\titlespacing*{\chapter}{0pt}{3pc}{5pc}
\titleformat{\section}{\normalfont\Large\bfseries}{\thesection}{.75em}{}
\titlespacing*{\section}{0pt}{3.5ex plus 1ex minus .2ex}{2ex plus .2ex}
\titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection}{.75em}{}
\titlespacing*{\subsection}{0pt}{3ex plus .8ex minus .2ex}{1.4ex plus .2ex}
\titleformat{\subsubsection}{\normalfont\normalsize\bfseries}{\thesubsubsection}{.75em}{}
\titlespacing*{\subsubsection}{0pt}{2.5ex plus .6ex minus .2ex}{1ex plus .2ex}
% A run-in heading (`**Span as the smallest containing subspace.**`) keeps its period.
\titleformat{\paragraph}[runin]{\normalfont\normalsize\bfseries}{}{0pt}{}
\titlespacing*{\paragraph}{0pt}{1.5ex plus .5ex minus .2ex}{.5em}
\newcommand\bookruninhead[1]{\paragraph{#1}}
\newcommand\booksubsectionhead[1]{\subsection*{#1}}
\newcommand\bookmath[1]{$#1$}
\setcounter{tocdepth}{1}

% A thematic break (`---` in a post).
\newcommand\textbreak{\par\medskip\centerline{\textasteriskcentered\quad\textasteriskcentered\quad\textasteriskcentered}\medskip}

% The books a section draws on (source_note), at its end, past a rule, as on the site.
\newcommand\sourcenote[1]{%
  \par\addvspace{1.5\baselineskip}%
  \begingroup\small\noindent\rule[.3\baselineskip]{4pc}{.4pt}\par\nobreak
  \noindent #1\par\endgroup}

%% -- Running heads: the chapter on the left page, the section on the right.
\RequirePackage{fancyhdr}
\RequirePackage{emptypage}
\pagestyle{fancy}
\fancyhf{}
\renewcommand\headrulewidth{0pt}
\fancyhead[LE,RO]{\small\thepage}
\fancyhead[CE]{\small\scshape\textls[30]{\nouppercase{\leftmark}}}
\fancyhead[CO]{\small\scshape\textls[30]{\nouppercase{\rightmark}}}
\renewcommand\chaptermark[1]{\markboth{\if@mainmatter\thechapter.\enspace\fi#1}{}}
\renewcommand\sectionmark[1]{\markright{\thesection.\enspace#1}}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\thepage}}

%% -- Footnotes stay at the foot of the page, ragged bottom or not.
\RequirePackage[bottom,splitrule]{footmisc}
\interfootnotelinepenalty=9000

%% -- The index of the terms definitions introduce (\emph in a definition).
\RequirePackage[noautomatic]{imakeidx}
\newcommand\makebookindex{%
  \makeindex[intoc, columns=2, columnsep=1.5pc]%
  \indexsetup{level=\chapter*, toclevel=chapter, firstpagestyle=plain,
    headers={\indexname}{\indexname}}}

%% -- Links and the PDF's outline.
\RequirePackage{xcolor}
\definecolor{extlink}{rgb}{0,0,1}
\RequirePackage[unicode, pdfpagelabels, bookmarksnumbered, bookmarksopen,
  bookmarksopenlevel=0, linktoc=all, colorlinks, linkcolor=extlink, urlcolor=extlink,
  citecolor=extlink, pdfdisplaydoctitle]{hyperref}
\RequirePackage{bookmark}
\urlstyle{same}

%% -- The title page and its verso.
\newcommand*\ext@title{}
\newcommand*\ext@author{}
\newcommand*\ext@site{}
\newcommand*\ext@url{}
\newcommand*\ext@date{}
\newcommand*\ext@years{}
\newcommand\booktitle[1]{\def\ext@title{#1}}
\newcommand\bookauthor[1]{\def\ext@author{#1}}
\newcommand\booksite[2]{\def\ext@site{#1}\def\ext@url{#2}}
\newcommand\bookdate[1]{\def\ext@date{#1}}
\newcommand\bookyears[1]{\def\ext@years{#1}}
\AtBeginDocument{\hypersetup{pdftitle={\ext@title}, pdfauthor={\ext@author}}}

\newcommand\ext@hostof[1]{\expandafter\ext@host#1\relax}
\def\ext@host#1://#2\relax{#2}
\newcommand\maketitlepages{%
  \begin{titlepage}
    \raggedright
    \vspace*{8pc}
    {\fontsize{38}{44}\selectfont\ext@title\par}
    \vspace{2.5pc}
    {\Large\ext@author\par}
    \vfill
    {\large\scshape\textls[80]{\MakeLowercase{\ext@site}}\par}
    \vspace{.3pc}
    {\href{\ext@url}{\ext@hostof{\ext@url}}\par}
  \end{titlepage}
  \thispagestyle{empty}
  \null\vfill
  \begingroup\small\raggedright\setlength{\parskip}{.8\baselineskip}%
    Copyright \textcopyright\ \ext@years\ \ext@author

    Typeset from the \ext@title\ notes on \emph{\ext@site},\\
    \url{\ext@url}, where they keep being revised.

    Licensed, like the notes, under the Creative Commons\\
    Attribution-NonCommercial-ShareAlike 4.0 International License\\
    (CC~BY-NC-SA~4.0), \url{https://creativecommons.org/licenses/by-nc-sa/4.0/}.

    Typeset on \ext@date\ with Lua\LaTeX\ in New Computer Modern.\par
  \endgroup
  \cleardoublepage}
\endinput
