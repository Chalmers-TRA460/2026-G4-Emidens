import type { SessionRun, AgentCardData } from "./types";

export const mockRun: SessionRun = {
  id: "run_47_card_2024",
  query:
    "What is the current evidence for SGLT2 inhibitors in reducing cardiovascular mortality in patients with HFrEF, and how do the benefits compare across different subgroups including diabetic vs non-diabetic patients?",
  status: "completed",
  statusLabel: "Completed",
  finishedAgo: "12 minutes ago",
  overview: {
    runId: "run_47_card_2024",
    started: "April 23, 2:34 PM",
    duration: "12 minutes",
    agents: ["Planner", "Evidence", "Analysis", "Summary"],
    timeline: [
      { label: "Query received", time: "2:34 PM", active: true },
      { label: "Planner Agent", time: "2:34 PM", active: true },
      { label: "Evidence Agent", time: "2:35 PM", active: true },
      { label: "Analysis Agent", time: "2:38 PM", active: true },
      { label: "Summary Agent", time: "2:45 PM", active: true },
      { label: "Run completed", time: "2:46 PM", active: true },
    ],
  },
  source: {
    title: "Empagliflozin in Heart Failure with Reduced Ejection Fraction",
    journal: "New England Journal of Medicine",
    year: "2020",
    volume: "Vol 383:15",
    page: "Page 8",
    sections: [
      { type: "heading", text: "Results" },
      {
        type: "paragraph",
        text: 'A total of 3730 patients underwent randomization, with 1863 assigned to receive empagliflozin and 1867 to receive placebo. During a median of 16 months of follow-up, a primary outcome event occurred in 361 of 1863 patients (19.4%) in the empagliflozin group and in 462 of 1867 patients (24.7%) in the placebo group (hazard ratio for cardiovascular death or hospitalization for heart failure, 0.75; 95% confidence interval [CI], 0.65 to 0.86; P<0.001).',
        highlights: [
          "0.75; 95% confidence interval [CI], 0.65 to 0.86; P<0.001",
        ],
      },
      {
        type: "paragraph",
        text: "The effect of empagliflozin on the primary outcome was consistent in patients with and those without diabetes (P=0.28 for interaction). There were 241 first hospitalizations for heart failure in the empagliflozin group, as compared with 318 in the placebo group (hazard ratio, 0.70; 95% CI, 0.58 to 0.85; P<0.001).",
        highlights: [
          "The effect of empagliflozin on the primary outcome was consistent in patients with and those without diabetes",
        ],
      },
      {
        type: "table",
        table: {
          caption: "Table 2. Primary and Secondary Outcomes",
          headers: ["Outcome", "Empagliflozin", "Placebo", "HR (95% CI)"],
          rows: [
            {
              cells: [
                "Primary outcome",
                "361 (19.4%)",
                "462 (24.7%)",
                "0.75 (0.65–0.86)",
              ],
              highlighted: true,
            },
            {
              cells: [
                "CV death",
                "187 (10.0%)",
                "202 (10.8%)",
                "0.92 (0.75–1.12)",
              ],
            },
            {
              cells: [
                "HF hospitalization",
                "241 (12.9%)",
                "318 (17.0%)",
                "0.70 (0.58–0.85)",
              ],
              highlighted: true,
            },
          ],
        },
      },
      {
        type: "paragraph",
        text: "Deaths from cardiovascular causes occurred in 187 patients (10.0%) in the empagliflozin group and in 202 patients (10.8%) in the placebo group (hazard ratio, 0.92; 95% CI, 0.75 to 1.12).",
      },
    ],
  },
};

export const mockAgentCards: AgentCardData[] = [
  {
    agentName: "Planner Agent",
    timestamp: "2:34:12 PM",
    color: "blue",
    content: (
      <div className="text-sm text-gray-700 space-y-2">
        <div className="font-medium">Research Plan:</div>
        <ol className="space-y-1.5 list-decimal list-inside text-sm">
          <li>
            Search for systematic reviews and meta-analyses on SGLT2 inhibitors
            in HFrEF
          </li>
          <li>
            Identify major randomized controlled trials (EMPEROR-Reduced,
            DAPA-HF)
          </li>
          <li>
            Extract cardiovascular mortality outcomes and subgroup analyses
          </li>
          <li>Compare efficacy in diabetic vs non-diabetic populations</li>
          <li>Synthesize safety profile and clinical implications</li>
        </ol>
      </div>
    ),
  },
  {
    agentName: "Evidence Agent",
    timestamp: "2:35:03 PM",
    color: "green",
    content: (
      <div className="space-y-3 text-sm">
        <div className="text-gray-700">
          <span className="font-medium">Search Query:</span> "SGLT2 inhibitors
          AND heart failure reduced ejection fraction AND cardiovascular
          mortality"
        </div>
        <div className="bg-green-50 border border-green-200 rounded-md p-3">
          <div className="font-medium text-green-900 mb-1">
            Found 23 relevant studies
          </div>
          <div className="text-sm text-gray-700">
            Including 2 landmark trials (EMPEROR-Reduced, DAPA-HF), 4
            meta-analyses
          </div>
        </div>
      </div>
    ),
  },
  {
    agentName: "Analysis Agent",
    timestamp: "2:38:24 PM",
    color: "yellow",
    content: (
      <div className="space-y-3">
        <div>
          <div className="font-medium text-gray-900 mb-2 text-sm">
            Key Clinical Outcomes:
          </div>
          <div className="space-y-1.5 text-sm text-gray-700">
            <div className="flex items-start gap-2">
              <div className="w-1 h-1 rounded-full bg-gray-400 mt-2 flex-shrink-0" />
              <div>
                <span className="font-medium">Primary Outcome:</span> 25%
                reduction in CV death or HF hospitalization (HR 0.75, 95% CI
                0.65-0.86, P&lt;0.001)
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-1 h-1 rounded-full bg-gray-400 mt-2 flex-shrink-0" />
              <div>
                <span className="font-medium">HF Hospitalizations:</span> 30%
                relative risk reduction (HR 0.70, 95% CI 0.58-0.85)
              </div>
            </div>
          </div>
        </div>
        <div>
          <div className="font-medium text-gray-900 mb-2 text-sm">
            Subgroup Analysis:
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 text-sm text-gray-700">
            Benefit consistent in diabetic vs non-diabetic patients (P=0.28 for
            interaction)
          </div>
        </div>
      </div>
    ),
  },
  {
    agentName: "Summary Agent",
    timestamp: "2:45:51 PM",
    color: "purple",
    content: (
      <div className="bg-purple-50 border border-purple-200 rounded-md p-3">
        <div className="font-medium text-gray-900 mb-1.5 text-sm">
          Clinical Conclusion:
        </div>
        <div className="text-sm text-gray-700 leading-relaxed">
          SGLT2 inhibitors demonstrate robust evidence for reducing
          cardiovascular events in HFrEF patients, with benefits consistent
          regardless of diabetes status. Class I recommendation for HFrEF
          patients with NYHA Class II-IV symptoms.
        </div>
      </div>
    ),
  },
];
