"use client";

import React from "react";

interface Props {
  onSubmit?: (data: any) => void;
}

export default function ClinicalDataInput({ onSubmit }: Props) {
  const [formData, setFormData] = React.useState({
    age: 55,
    hba1c: 5.7,
    sex: "male",
    bmi: 27.0,
    serumCreatinine: 1.1,
    cystatinC: 0.9,
    systolicBP: 120,
    diastolicBP: 80,
    albumin: 4.0,
    crp: 1.5,
  });

  const handleChange = (name: string, value: any) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleStep = (name: string, step: number) => {
    setFormData((prev) => ({
      ...prev,
      [name]: parseFloat(((prev as any)[name] + step).toFixed(2)),
    }));
  };

  const Stepper = ({
    label,
    name,
    step = 0.1,
  }: {
    label: string;
    name: string;
    step?: number;
  }) => (
    <div>
      <label className="block text-sm mb-2 text-gray-300">{label}</label>
      <div className="flex items-center bg-gray-900 rounded-xl px-4 py-2 border border-gray-800">
        <button
          type="button"
          onClick={() => handleStep(name, -step)}
          className="text-gray-400 hover:text-white px-3 text-lg"
        >
          −
        </button>

        <input
          type="number"
          value={(formData as any)[name]}
          onChange={(e) => handleChange(name, parseFloat(e.target.value))}
          className="w-full bg-transparent text-center text-white outline-none"
        />

        <button
          type="button"
          onClick={() => handleStep(name, step)}
          className="text-gray-400 hover:text-white px-3 text-lg"
        >
          +
        </button>
      </div>
    </div>
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSubmit) onSubmit(formData);
  };

  return (
    <div className="min-h-screen bg-black text-white px-6 py-12">
      <h2 className="text-3xl font-bold mb-2">🧪 CKD Staging Input Panel</h2>
      <p className="text-gray-400 mb-10">
        Enter patient parameters below to estimate eGFR and CKD Stage.
      </p>

      <form onSubmit={handleSubmit} className="grid md:grid-cols-2 gap-12">
        {/* ================= COLUMN 1 ================= */}
        <div className="space-y-8">
          {/* RANGE 1 — AGE */}
          <div>
            <label className="block text-sm mb-2 text-gray-300">
              Patient Age:
              <span className="text-red-500 font-semibold ml-2">
                {formData.age}
              </span>
            </label>
            <input
              type="range"
              min="18"
              max="95"
              value={formData.age}
              onChange={(e) => handleChange("age", parseInt(e.target.value))}
              className="w-full accent-red-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>18</span>
              <span>95</span>
            </div>
          </div>

          {/* 4 FIELDS BELOW */}
          <div className="space-y-6">
            {/* Sex */}
            <div>
              <label className="block text-sm mb-2 text-gray-300">Sex</label>
              <select
                value={formData.sex}
                onChange={(e) => handleChange("sex", e.target.value)}
                className="w-full bg-gray-900 border border-gray-800 rounded-xl px-4 py-2 text-white"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>

            <Stepper label="BMI (kg/m²)" name="bmi" />
            <Stepper label="Serum Creatinine (mg/dL)" name="serumCreatinine" />
            <Stepper label="Serum Cystatin C (mg/L)" name="cystatinC" />
          </div>
        </div>

        {/* ================= COLUMN 2 ================= */}
        <div className="space-y-8">
          {/* RANGE 2 — HbA1c */}
          <div>
            <label className="block text-sm mb-2 text-gray-300">
              HbA1c (%):
              <span className="text-red-500 font-semibold ml-2">
                {formData.hba1c.toFixed(2)}
              </span>
            </label>
            <input
              type="range"
              min="4"
              max="15"
              step="0.1"
              value={formData.hba1c}
              onChange={(e) =>
                handleChange("hba1c", parseFloat(e.target.value))
              }
              className="w-full accent-red-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>4.00</span>
              <span>15.00</span>
            </div>
          </div>

          {/* 4 FIELDS BELOW */}
          <div className="space-y-6">
            <Stepper label="Systolic BP (mmHg)" name="systolicBP" step={1} />
            <Stepper label="Diastolic BP (mmHg)" name="diastolicBP" step={1} />
            <Stepper label="Albumin (g/dL)" name="albumin" />
            <Stepper label="CRP (mg/L)" name="crp" />
          </div>
        </div>

        {/* SUBMIT FULL WIDTH */}
        <div className="md:col-span-2 mt-10">
          <button
            type="submit"
            className="w-full bg-red-600 hover:bg-red-700 transition py-3 rounded-xl font-semibold text-lg shadow-lg"
          >
            Calculate Risk Analysis
          </button>
        </div>
      </form>
    </div>
  );
}
