import pytest
import topside as top


def test_procedure_latex_export():
    s1 = top.ProcedureStep('s1', top.Action("remote fill valve", "open"), [])
    s2 = top.ProcedureStep('s2', top.Action("remote vent valve", "closed"), [])

    proc = top.Procedure('p1', [s1, s2])

    export = proc.export("latex")

    print(export)

    expected_export = r"""\subsection{p1}
\begin{checklist}
    \item Open remote fill valve
    \item Close remote vent valve
\end{checklist}"""
    print(expected_export)
    assert export == expected_export
