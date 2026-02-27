"""
Construct-level checks: modality-driven blueprint generation.
"""

from typing import Dict, List, Optional

from .models import ConstructBlueprint, Domain, ModalityEnum


class ConstructChecker:
    """Generates abstract construct blueprints based on modality."""

    @staticmethod
    def generate_blueprint(
        project_name: str,
        modality: str,
        sequence: str,
        expression_system: str
    ) -> ConstructBlueprint:
        """
        Generate an abstract construct blueprint.
        
        Does NOT provide lab assembly steps, only the abstract architecture.
        """
        if modality == ModalityEnum.IgG_like_bispecific.value:
            return ConstructChecker._blueprint_igg_bispecific(project_name, sequence, expression_system)
        elif modality == ModalityEnum.VHH_bispecific.value:
            return ConstructChecker._blueprint_vhh_bispecific(project_name, sequence, expression_system)
        elif modality == ModalityEnum.Fab_scFv.value:
            return ConstructChecker._blueprint_fab_scfv(project_name, sequence, expression_system)
        elif modality == ModalityEnum.Fc_fusion.value:
            return ConstructChecker._blueprint_fc_fusion(project_name, sequence, expression_system)
        else:
            return ConstructBlueprint(chains=[], warnings=[f"Unknown modality: {modality}"])

    @staticmethod
    def _blueprint_igg_bispecific(
        project_name: str,
        sequence: str,
        expression_system: str
    ) -> ConstructBlueprint:
        """
        IgG-like bispecific: 2x2 array (HC1, LC1, HC2, LC2) + optional Fc.
        """
        seq_len = len(sequence.strip().upper())
        
        domains = [
            Domain(chain="HC1", name="VH1", start=None, end=None),
            Domain(chain="HC1", name="CH1", start=None, end=None),
            Domain(chain="LC1", name="VL1", start=None, end=None),
            Domain(chain="LC1", name="CL", start=None, end=None),
            Domain(chain="HC2", name="VH2", start=None, end=None),
            Domain(chain="HC2", name="CH1", start=None, end=None),
            Domain(chain="LC2", name="VL2", start=None, end=None),
            Domain(chain="LC2", name="CL", start=None, end=None),
        ]
        
        warnings = []
        if seq_len > 400:
            warnings.append("Large IgG construct; consider modularization for manufacturability")
        
        if expression_system == "ecoli":
            warnings.append("E. coli expression of IgG-like constructs may require special strains or periplasmic expression")
        
        return ConstructBlueprint(
            chains=["HC1", "LC1", "HC2", "LC2"],
            domains=domains,
            warnings=warnings
        )

    @staticmethod
    def _blueprint_vhh_bispecific(
        project_name: str,
        sequence: str,
        expression_system: str
    ) -> ConstructBlueprint:
        """
        VHH bispecific: single-chain [VHH1–Linker–VHH2].
        """
        seq_len = len(sequence.strip().upper())
        
        domains = [
            Domain(chain="ScVHH", name="VHH1", start=None, end=None),
            Domain(chain="ScVHH", name="Linker", start=None, end=None),
            Domain(chain="ScVHH", name="VHH2", start=None, end=None),
        ]
        
        warnings = []
        if seq_len > 350:
            warnings.append("Long VHH-VHH fusion; linker length optimization recommended")
        
        if seq_len < 180:
            warnings.append("Sequence may be too short for VHH bispecific construct")
        
        return ConstructBlueprint(
            chains=["ScVHH"],
            domains=domains,
            warnings=warnings
        )

    @staticmethod
    def _blueprint_fab_scfv(
        project_name: str,
        sequence: str,
        expression_system: str
    ) -> ConstructBlueprint:
        """
        Fab + scFv: hybrid format.
        """
        seq_len = len(sequence.strip().upper())
        
        domains = [
            Domain(chain="Fab_HC", name="VH", start=None, end=None),
            Domain(chain="Fab_HC", name="CH1", start=None, end=None),
            Domain(chain="Fab_LC", name="VL", start=None, end=None),
            Domain(chain="Fab_LC", name="CL", start=None, end=None),
            Domain(chain="scFv", name="scFv", start=None, end=None),
        ]
        
        warnings = []
        if seq_len > 500:
            warnings.append("Very large Fab-scFv fusion; expression yield may be reduced")
        
        return ConstructBlueprint(
            chains=["Fab_HC", "Fab_LC", "scFv"],
            domains=domains,
            warnings=warnings
        )

    @staticmethod
    def _blueprint_fc_fusion(
        project_name: str,
        sequence: str,
        expression_system: str
    ) -> ConstructBlueprint:
        """
        Fc fusion: [Binder–Linker–Fc].
        """
        seq_len = len(sequence.strip().upper())
        
        domains = [
            Domain(chain="Fusion", name="Binder", start=None, end=None),
            Domain(chain="Fusion", name="Linker", start=None, end=None),
            Domain(chain="Fusion", name="Fc", start=None, end=None),
        ]
        
        warnings = []
        if expression_system == "ecoli":
            warnings.append("Fc domain typically requires mammalian glycosylation; E. coli may not be ideal")
        
        if seq_len < 200:
            warnings.append("Binder portion may be very small; verify adequacy for target binding")
        
        return ConstructBlueprint(
            chains=["Fusion"],
            domains=domains,
            warnings=warnings
        )
