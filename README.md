# Scenario-Clustering

Decision-making under uncertainty often relies on scenario-based stochastic optimization, where a large set of possible scenarios is used to approximate random outcome distributions. However, using all generated scenarios can make optimization intractable. Scenario reduction techniques address this by selecting or aggregating a smaller representative subset of scenarios that preserves the essential characteristics of the full set.

Clustering-based scenario reduction is a popular approach: similar scenarios (by probability distribution or outcomes) are grouped, and representative scenarios are selected from each cluster. This reduces the scenario count while aiming to maintain accuracy. Traditionally, reduction focused on statistical similarity (distance between scenarios), but recent methods increasingly incorporate the optimization problem’s structure and objective into the reduction process [Bertsimas et al. (2022)](https://pubsonline.informs.org/doi/abs/10.1287/opre.2022.2265?casa_token=trhGHK1R1-0AAAAA:Vw4y-1SSIIEcCiErwzdKOb52qy3mVl54BofxMnNBURTYxYSQ49MNAYJOiuJXJaTxMxD3DXM92CI).

In modular construction planning for a multi-brand developer, robust ecosystem orchestration is critical. The problem faces inherent demand uncertainty and large scale (1000 scenarios × 751 projects). Directly optimizing over all scenarios is computationally infeasible. Therefore, scenario clustering is used to reduce dimensionality while preserving the diversity and key characteristics of demand data.

This project proposes a new clustering algorithm, benchmarking it against existing methods. It also reviews recent methodologies, evaluation metrics, and practical applications.

For a visual overview, see the [video demonstration](https://drive.google.com/drive/folders/1AgZ_KLPOhzpIjqF8WgUsjw2z8tk0Se8E?usp=sharing).
