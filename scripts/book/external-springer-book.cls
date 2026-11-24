%% Default book design: Springer Nature SNmono v6.00 on the approved compact trim.
%% The publisher class is kept unmodified in vendor/springer. Typeset with LuaLaTeX.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{external-springer-book}[2026/11/15 SNmono book edition]
% SNmono loads amsthm itself. amsmath must precede it for QED marks in align.
\RequirePackage{amsmath}
\LoadClass[graybox,envcountsect,envcountsame,sectrefs]{SNmono}

% LuaTeX does not expose pdfTeX's legacy glyph-to-Unicode primitives by default.
% Enable the mappings before NewTX loads, so its Type 1 math fonts remain copyable.
\ifdefined\pdfglyphtounicode\else
  \protected\def\pdfglyphtounicode{\pdfextension glyphtounicode }%
\fi
\ifdefined\pdfgentounicode\else
  \protected\edef\pdfgentounicode{\pdfvariable gentounicode}%
\fi
\pdfgentounicode=1
\input{glyphtounicode}
\input{glyphtounicode-cmr}
\input{glyphtounicode-ntx}

%% The sample package's recommended Times text and math. Do not load the original
%% external-book class: its fonts, titles and running heads would replace SNmono's.
\RequirePackage{newtxtext}
\RequirePackage[varvw]{newtxmath}
\RequirePackage{mathtools}
\RequirePackage[final]{microtype}
\RequirePackage{graphicx}
% Termes lacks several IPA letters used in the notes' pronunciation footnotes.
% Use the original face for those characters only, preserving the text verbatim.
\RequirePackage{newunicodechar}
\newfontfamily\ext@ipafont{NewCM10-Book.otf}
\newunicodechar{ˈ}{{\ext@ipafont\char"02C8}}
\newunicodechar{ɪ}{{\ext@ipafont\char"026A}}
\newunicodechar{ʊ}{{\ext@ipafont\char"028A}}
\newunicodechar{ʃ}{{\ext@ipafont\char"0283}}
\newunicodechar{ɡ}{{\ext@ipafont\char"0261}}
\newunicodechar{ɑ}{{\ext@ipafont\char"0251}}
\newunicodechar{ː}{{\ext@ipafont\char"02D0}}
% site-macros.tex draws \whitestar as the site shows it, centred on NewTX's math axis.
\input{site-macros}

%% Approved book format: keep SNmono's text block on a compact 155 x 235 mm page.
%% Body margins are inner20, outer18, top20 and bottom24 mm; heads/folios are separate.
\RequirePackage[paperwidth=155mm,paperheight=235mm,textwidth=117mm,textheight=191mm,
  inner=20mm,top=20mm,headheight=12pt,headsep=12pt,footskip=24pt]{geometry}
\setlength{\emergencystretch}{3em}
\allowdisplaybreaks[1]
% Only long inline tuple candidates get comma breaks. Keep short expressions such
% as C(R,R) together; measuring here respects the current font and local line width.
\mathchardef\ext@mathcomma=\mathcode`\,
\begingroup\lccode`\~=`\,
\lowercase{\endgroup\def~}{\ext@mathcomma\allowbreak}
\newcommand\bookmath[1]{\begingroup
  \setbox\z@=\hbox{$#1$}%
  \ifdim\wd\z@>.35\linewidth\mathcode`\,="8000\fi
  $#1$\endgroup}

%% Native Springer theorem layout, with labels supplied by the site rather than
%% generated counters. This preserves every existing statement number and link.
\newcommand*\ext@unithead{}
\spnewtheorem*{ext@plain}{\noexpand\ext@unithead}{\bfseries}{\itshape}
\spnewtheorem*{ext@definition}{\noexpand\ext@unithead}{\bfseries}{\rmfamily}
\spnewtheorem*{ext@remark}{\noexpand\ext@unithead}{\itshape}{\rmfamily}
\def\ext@headkind#1 #2\@nil{\def\ext@kind{#1}}
\NewDocumentEnvironment{statement}{m m o}
  {\def\ext@unithead{#2}\def\ext@style{#1}%
   \expandafter\ext@headkind#2 \@nil
   \@for\ext@italichead:=Example,Remark,Note,Claim,Case,Conjecture,Property,Question\do{%
     \ifx\ext@kind\ext@italichead\def\ext@style{remark}\fi}%
   \IfNoValueTF{#3}{\begin{ext@\ext@style}}{\begin{ext@\ext@style}[#3]}}
  {\end{ext@\ext@style}}
\renewcommand\qedsymbol{\ensuremath{\square}}
\newcommand\noqed{\renewcommand\qedsymbol{}}
\NewDocumentEnvironment{subproof}{O{Subproof}}
  {\begin{proof}[#1]\renewcommand\qedsymbol{\ensuremath{\blacksquare}}}
  {\end{proof}}
\newcommand\qedsymbolhere[1]{{\renewcommand\qedsymbol{\ensuremath{#1}}\qed}}
\newcommand\unitlabel[1]{\phantomsection\label{#1}}

%% The writer's list options encode source labels and start values. Retain that
%% interface, with upright source labels, without importing external-book spacing.
\RequirePackage{enumitem}
\setlist{font=\upshape,labelindent=0pt,labelsep=.5em,leftmargin=*,align=left}
\setlist[enumerate,1]{label=(\arabic*),widest=99}
\setlist[enumerate,2]{label=(\alph*)}
\setlist[enumerate,3]{label=(\roman*)}
\setlist[enumerate,4]{label=(\Alph*)}
\RequirePackage{tikz-cd}
% A figure is numbered as its label reads; SNmono sets the caption.
\newcommand\figurecaption[2]{\renewcommand\thefigure{#1}\caption{#2}}
\RequirePackage[bottom,splitrule]{footmisc}
% Keep ordinary notes together with a strong preference, but retain a safe split
% for notes too large for a page. splitrule identifies a continued footnote.
\interfootnotelinepenalty=9000
% A source subheading is a numbered subsection with SNmono's native run-in
% typography. Its counter resets at every section; statement numbers stay literal.
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
  {-6\p@}{-6\p@}%
  {\normalfont\normalsize\bfseries\boldmath
   \rightskip=\z@\@plus8em\pretolerance=10000 }}
\setcounter{secnumdepth}{2}
\newcommand\bookruninhead[1]{\subsection{#1}}
\newcommand\booksubsectionhead[1]{\subsection{#1}}
\newcommand\textbreak{\par\medskip\centerline{\textasteriskcentered\quad\textasteriskcentered\quad\textasteriskcentered}\medskip}
\newcommand\sourcenote[1]{\par\addvspace{1.5\baselineskip}%
  \begingroup\small\noindent #1\par\endgroup}

%% Use the publisher's two-column index and MakeIndex style.
\RequirePackage{multicol}
\RequirePackage[noautomatic,original]{imakeidx}
\newcommand\makebookindex{\makeindex}
\setcounter{tocdepth}{2}
\RequirePackage{xcolor}
\definecolor{extlink}{rgb}{0,0,1}
\RequirePackage[unicode,pdfpagelabels,bookmarksnumbered,bookmarksopen,
  bookmarksopenlevel=0,linktoc=all,colorlinks,linkcolor=extlink,urlcolor=extlink,
  citecolor=extlink,pdfdisplaydoctitle]{hyperref}
\RequirePackage{bookmark}
\urlstyle{same}

%% Native title typography, with the site's identity in place of the publisher
%% imprint printed by the sample macro. This is an independent comparison edition.
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
\AtBeginDocument{\hypersetup{pdftitle={\ext@title},pdfauthor={\ext@author}}}
\RequirePackage{etoolbox}
\patchcmd{\@maketitle}{{\Large Springer Nature\par}}{{\Large\ext@site\par}}{}%
  {\ClassError{external-springer-book}{SNmono title imprint could not be adapted}{Check the vendored SNmono version.}}
\newcommand\maketitlepages{%
  \setcounter{page}{1}% SNmono reserves four unprovided publisher front-matter pages.
  \begingroup\author{\ext@author}\title{\ext@title}\date{}\maketitle\endgroup
  \clearpage\thispagestyle{empty}\null\vfill
  \begingroup\small\raggedright\setlength{\parskip}{.8\baselineskip}%
    Copyright \textcopyright\ \ext@years\ \ext@author

    Typeset from the \ext@title\ notes on \emph{\ext@site},\\
    \url{\ext@url}, where they keep being revised.

    Licensed, like the notes, under the Creative Commons\\
    Attribution-NonCommercial-ShareAlike 4.0 International License\\
    (CC~BY-NC-SA~4.0), \url{https://creativecommons.org/licenses/by-nc-sa/4.0/}.

    Independent edition using the Springer Nature\\
    SNmono template v6.00 and NewTX text and mathematics.

    Typeset on \ext@date\ with Lua\LaTeX.\par
  \endgroup\cleardoublepage}
\endinput
