/-
  Formal Symbolic Systems Theory - Drift/coupling theorems.

  Status: candidate cross-module theorem surface / stage 1 / do not promote.

  Purpose:
    Compose the older SymbolicSystem formalization cluster:

      Drift -> Correction -> ValidityLayers -> RealityCoupling

    The key discipline in this file is avoiding an overclaim. Losing fidelity
    to one referent does not by itself imply total coupling loss: a drifted
    symbol may still be coupled to another in-scope, action-relevant referent.
    Coupling loss requires a stronger no-coupling or null-referent condition.

  Non-claims:
    1. Drift loss to one referent is not treated as total coupling loss.
    2. No quantitative drift or coupling model is introduced.
    3. No bridge to margin/stacking is asserted here.
-/

import Core.Correction
import Core.Drift
import Core.RealityCoupling
import Core.ValidityLayers

namespace FSST

open FSST

def DriftedReferentFidelityLost
    (sys : SymbolicSystem)
    (r : sys.Referent)
    (s : sys.Symbol)
    (n : Nat) : Prop :=
  sys.fidelity r s /\
    Not (sys.fidelity r (sys.drift s n))

def DriftCorrectionCouplingResilient
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys) : Prop :=
  CorrectionDominatesDrift sys /\
    forall r : sys.Referent,
      forall s : sys.Symbol,
        forall n : Nat,
          sys.scope r ->
          sys.fidelity r s ->
          cm.actionRelevant r ->
          cm.coupling (sys.correct (sys.drift s n)) > 0 ->
          RealityCoupled sys cm (sys.correct (sys.drift s n))

theorem drift_loss_is_referent_relative
    (sys : SymbolicSystem)
    (r : sys.Referent)
    (s : sys.Symbol)
    (n : Nat)
    (hfid : sys.fidelity r s)
    (hlost : Not (sys.fidelity r (sys.drift s n))) :
    DriftedReferentFidelityLost sys r s n := by
  exact And.intro hfid hlost

theorem drifted_referential_null_implies_coupling_lost
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (s : sys.Symbol)
    (n : Nat)
    (hnull : ReferentiallyNull sys (sys.drift s n)) :
    CouplingLost sys cm (sys.drift s n) := by
  constructor
  · trivial
  · intro ⟨r, _hscope, hfid, _hrelevant, _hpositive⟩
    exact hnull r hfid

theorem drifted_symbol_coupling_loss_requires_no_alternate_coupling
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (s : sys.Symbol)
    (n : Nat)
    (hnot : Not (RealityCoupled sys cm (sys.drift s n))) :
    CouplingLost sys cm (sys.drift s n) := by
  exact And.intro trivial hnot

theorem correction_dominance_restores_drifted_coupling
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (hcorr : CorrectionDominatesDrift sys)
    (r : sys.Referent)
    (s : sys.Symbol)
    (n : Nat)
    (hscope : sys.scope r)
    (hfid : sys.fidelity r s)
    (hrelevant : cm.actionRelevant r)
    (hpositive : cm.coupling (sys.correct (sys.drift s n)) > 0) :
    RealityCoupled sys cm (sys.correct (sys.drift s n)) := by
  exact ⟨r, hscope, hcorr r s n hscope hfid, hrelevant, hpositive⟩

theorem maintained_system_restores_drifted_coupling
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (hmaintained : MaintainedSystem sys)
    (r : sys.Referent)
    (s : sys.Symbol)
    (n : Nat)
    (hscope : sys.scope r)
    (hfid : sys.fidelity r s)
    (hrelevant : cm.actionRelevant r)
    (hpositive : cm.coupling (sys.correct (sys.drift s n)) > 0) :
    RealityCoupled sys cm (sys.correct (sys.drift s n)) := by
  exact correction_dominance_restores_drifted_coupling
    sys cm hmaintained.left r s n hscope hfid hrelevant hpositive

theorem resilience_from_correction_dominance
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (hcorr : CorrectionDominatesDrift sys) :
    DriftCorrectionCouplingResilient sys cm := by
  constructor
  · exact hcorr
  · intro r s n hscope hfid hrelevant hpositive
    exact correction_dominance_restores_drifted_coupling
      sys cm hcorr r s n hscope hfid hrelevant hpositive

end FSST
