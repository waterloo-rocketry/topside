import pytest
import topside as top
import os


def test_procedure_latex_export():
    s1 = top.ProcedureStep('s1', top.StateChangeAction('remote fill valve', 'open'), [], 'PRIMARY')
    s2 = top.ProcedureStep('s2', top.StateChangeAction(
        'remote vent valve', 'closed'), [], 'SECONDARY')

    proc = top.Procedure('p1', [s1, s2])

    export = proc.export('latex')

    expected_export = r'''\subsection{p1}
\begin{checklist}
    \item \PRIMARY{} Open remote fill valve
    \item \SECONDARY{} Close remote vent valve
\end{checklist}'''
    assert export == expected_export


def test_procedure_suite_latex_export():
    s1 = top.ProcedureStep('s1', top.StateChangeAction('remote fill valve', 'open'), [], 'PRIMARY')
    s2 = top.ProcedureStep('s2', top.StateChangeAction(
        'remote vent valve', 'closed'), [], 'SECONDARY')

    proc_main = top.Procedure('main', [s1, s2])
    proc_abort = top.Procedure('abort', [s2])

    suite = top.ProcedureSuite([proc_main, proc_abort])

    export = suite.export('latex')

    expected_export = r'''\subsection{main}
\begin{checklist}
    \item \PRIMARY{} Open remote fill valve
    \item \SECONDARY{} Close remote vent valve
\end{checklist}

\subsection{abort}
\begin{checklist}
    \item \SECONDARY{} Close remote vent valve
\end{checklist}'''

    assert export == expected_export


def test_waituntil_latex_export():
    suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.WaitUntil(10e6), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'PRIMARY')
        ])
    ])

    export = suite.export('latex')

    print(export)

    expected_export = r'''\subsection{main}
\begin{checklist}
    \item \PRIMARY{} Open injector\_valve
    \item Wait 10 seconds
    \item \PRIMARY{} Close vent\_valve
\end{checklist}'''

    assert export == expected_export


def test_proclang_file_latex_export():
    filepath = os.path.join(os.path.dirname(__file__), 'example.proc')
    export = top.proclang.parse_from_file(filepath).export('latex')

    # Need to add newline to export since the tex file ends with a newline
    export += '\n'

    expected_export = ''
    with open('example.tex', 'r') as f:
        expected_export = f.read()

    assert export == expected_export


def test_waituntil_latex_export():
    suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.And([top.WaitUntil(10e6), top.Or([top.Less('p1', 400.0),
                                                       top.GreaterEqual('p2', 17.0)])]), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'PRIMARY')
        ])
    ])

    export = suite.export('latex')

    print(export)

    expected_export = r'''\subsection{main}
\begin{checklist}
    \item \PRIMARY{} Open injector\_valve
    \item Wait 10 seconds and p1 is less than 400psi or p2 is greater than or equal to 17psi
    \item \PRIMARY{} Close vent\_valve
\end{checklist}'''

    assert export == expected_export
