import { useState } from "react";
import type { ClinicalContext } from "../../../api/stream";

interface ClinicalInputFormProps {
  fields: string[];
  onSubmit: (ctx: ClinicalContext, skippedFields?: string[]) => void;
  disabled?: boolean;
}

const FIELD_LABELS: Record<string, string> = {
  age_years:           "Age (years)",
  weight_kg:           "Weight (kg)",
  renal_impairment:    "Renal impairment",
  hepatic_impairment:  "Hepatic impairment",
  active_conditions:   "Active conditions",
  current_medications: "Current medications",
};

const FIELD_HINTS: Record<string, string> = {
  active_conditions:   "Comma-separated, e.g. atrial fibrillation, CKD stage 3",
  current_medications: "Comma-separated, e.g. amiodarone, ramipril",
};

type FormState = {
  age_years?:           string;
  weight_kg?:           string;
  renal_impairment?:    boolean;
  hepatic_impairment?:  boolean;
  active_conditions?:   string;
  current_medications?: string;
};

const TEXT_OR_NUMBER_FIELDS = new Set([
  "age_years",
  "weight_kg",
  "active_conditions",
  "current_medications",
]);

function emptyFields(state: FormState, fields: string[]): string[] {
  return fields.filter((f) => {
    if (!TEXT_OR_NUMBER_FIELDS.has(f)) return false;
    const v = state[f as keyof FormState];
    return typeof v !== "string" || v.trim() === "";
  });
}

function toContext(state: FormState, fields: string[]): ClinicalContext {
  const ctx: ClinicalContext = {};
  for (const f of fields) {
    if (f === "age_years" && state.age_years) {
      const n = Number(state.age_years);
      if (!Number.isNaN(n)) ctx.age_years = n;
    } else if (f === "weight_kg" && state.weight_kg) {
      const n = Number(state.weight_kg);
      if (!Number.isNaN(n)) ctx.weight_kg = n;
    } else if (f === "renal_impairment") {
      ctx.renal_impairment = !!state.renal_impairment;
    } else if (f === "hepatic_impairment") {
      ctx.hepatic_impairment = !!state.hepatic_impairment;
    } else if (f === "active_conditions" && state.active_conditions) {
      ctx.active_conditions = state.active_conditions
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    } else if (f === "current_medications" && state.current_medications) {
      ctx.current_medications = state.current_medications
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    }
  }
  return ctx;
}

export function ClinicalInputForm({ fields, onSubmit, disabled }: ClinicalInputFormProps) {
  const [state, setState] = useState<FormState>({});
  const [pendingSkip, setPendingSkip] = useState<string[] | null>(null);

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setState((prev) => ({ ...prev, [key]: value }));
  };

  const submitNow = (skipped: string[]) => {
    onSubmit(toContext(state, fields), skipped.length > 0 ? skipped : undefined);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const empty = emptyFields(state, fields);
    if (empty.length > 0) {
      setPendingSkip(empty);
      return;
    }
    submitNow([]);
  };

  const labelFor = (f: string) => FIELD_LABELS[f] ?? f;

  if (pendingSkip) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3">
        <div className="text-sm font-medium text-amber-900">
          Answer without this information?
        </div>
        <div className="text-xs text-amber-900">
          The following fields are still empty:
          <ul className="list-disc list-inside mt-1">
            {pendingSkip.map((f) => <li key={f}>{labelFor(f)}</li>)}
          </ul>
          The agent will produce a best-effort answer with explicit safety caveats,
          and confidence will be reduced.
        </div>
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={() => setPendingSkip(null)}
            disabled={disabled}
            className="text-xs font-medium px-3 py-1.5 rounded-md bg-white border border-amber-300 text-amber-900 hover:bg-amber-100 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            Go back
          </button>
          <button
            type="button"
            onClick={() => submitNow(pendingSkip)}
            disabled={disabled}
            className="text-xs font-medium px-3 py-1.5 rounded-md bg-amber-600 text-white hover:bg-amber-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Answer anyway
          </button>
        </div>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3"
    >
      <div className="text-sm font-medium text-amber-900">
        Additional patient information requested
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {fields.map((field) => (
          <FieldInput
            key={field}
            field={field}
            state={state}
            update={update}
            disabled={disabled}
          />
        ))}
      </div>
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={disabled}
          className="text-xs font-medium px-3 py-1.5 rounded-md bg-amber-600 text-white hover:bg-amber-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          Re-run with these inputs
        </button>
      </div>
    </form>
  );
}

interface FieldInputProps {
  field: string;
  state: FormState;
  update: <K extends keyof FormState>(key: K, value: FormState[K]) => void;
  disabled?: boolean;
}

function FieldInput({ field, state, update, disabled }: FieldInputProps) {
  const label = FIELD_LABELS[field] ?? field;
  const hint = FIELD_HINTS[field];

  if (field === "renal_impairment" || field === "hepatic_impairment") {
    return (
      <label className="flex items-center gap-2 text-xs text-gray-800 sm:col-span-2">
        <input
          type="checkbox"
          checked={!!state[field]}
          onChange={(e) => update(field, e.target.checked)}
          disabled={disabled}
          className="rounded border-gray-300"
        />
        {label}
      </label>
    );
  }

  if (field === "age_years" || field === "weight_kg") {
    return (
      <label className="flex flex-col gap-1 text-xs text-gray-800">
        <span>{label}</span>
        <input
          type="number"
          inputMode="decimal"
          step={field === "weight_kg" ? "0.1" : "1"}
          min={0}
          value={state[field] ?? ""}
          onChange={(e) => update(field, e.target.value)}
          disabled={disabled}
          className="rounded border border-gray-300 px-2 py-1 bg-white"
        />
      </label>
    );
  }

  if (field === "active_conditions" || field === "current_medications") {
    return (
      <label className="flex flex-col gap-1 text-xs text-gray-800 sm:col-span-2">
        <span>{label}</span>
        <input
          type="text"
          value={state[field] ?? ""}
          onChange={(e) => update(field, e.target.value)}
          disabled={disabled}
          placeholder={hint}
          className="rounded border border-gray-300 px-2 py-1 bg-white"
        />
      </label>
    );
  }

  return (
    <div className="text-xs text-gray-500">Unknown field: {field}</div>
  );
}
