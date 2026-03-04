"use client";

import { useState } from "react";
import { Prediction } from "../types/prediction";

export default function usePrediction() {
  const [result, setResult] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);

  return { result, setResult, loading, setLoading };
}
