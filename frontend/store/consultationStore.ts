"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { Consultation } from "../types/prediction";

interface ConsultationContextType {
  consultations: Consultation[];
  setConsultations: (c: Consultation[]) => void;
}

const ConsultationContext = createContext<ConsultationContextType | undefined>(undefined);

export function ConsultationProvider({ children }: { children: ReactNode }) {
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  return <ConsultationContext.Provider value={{ consultations, setConsultations }}>{children}</ConsultationContext.Provider>;
}

export function useConsultations() {
  const ctx = useContext(ConsultationContext);
  if (!ctx) throw new Error("useConsultations must be used within ConsultationProvider");
  return ctx;
}
