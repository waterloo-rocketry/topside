import pytest
import topside as top


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

    print(export)

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
