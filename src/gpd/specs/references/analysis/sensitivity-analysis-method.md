# sensitivity-analysis

Identify the target quantity, parameter domains, baseline values and dependencies.
Distinguish local derivatives from global sensitivity over an explicit domain.
Use dimensionless sensitivities only when the normalization is defined; a zero
baseline needs an absolute or otherwise justified scale. Check finite-difference
step stability or use analytical derivatives. Handle parameter correlations,
interactions and constrained variation; rankings depend on ranges/distributions.
Near critical points or divergent derivatives, report the breakdown of linear
propagation instead of inventing finite uncertainty. Separate sensitivity from
uncertainty: derivatives alone do not define error bars. Ask for missing input
uncertainties only when uncertainty propagation is actually required. Investigate
all-zero derivatives, cancellation and dependency mistakes before concluding
insensitivity. Report method, ranking, approximation dependence and usable domain.
