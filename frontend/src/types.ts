export type ObjectType = 
  | "Text"
  | "Valve"
  | "Instrument"
  | "Dimension"
  | "Pipeline"
  | "Equipment"
  | "Annotation"
  | "Title Block"
  | "Notes";

export type ChangeType = "Added" | "Removed" | "Modified" | "Unchanged";

export interface CanonicalObject {
  id: str;
  type: ObjectType;
  tag?: string;
  text: string;
  page: number;
  bbox: number[];
  rotation?: number;
  layer?: string;
  font_size?: number;
  confidence: number;
  metadata?: Record<string, any>;
}

export interface DeltaItem {
  id: string;
  change_type: ChangeType;
  object_type: ObjectType;
  tag?: string;
  description: string;
  page_a?: number;
  page_b?: number;
  bbox_a?: number[];
  bbox_b?: number[];
  text_a?: string;
  text_b?: string;
  confidence: number;
  details?: Record<string, any>;
}

export interface DeltaResult {
  summary: {
    total_changes: number;
    added: number;
    removed: number;
    modified: number;
    unchanged: number;
  };
  overall_confidence: number;
  items: DeltaItem[];
}

export interface CompareResponse {
  session_id: string;
  ai_summary: string;
  delta_result: DeltaResult;
  telemetry: Record<string, any>;
}

export interface Citation {
  source: string;
  page?: number;
  tag?: string;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  groundedness_score: number;
  retrieved_contexts: any[];
  prompt_tokens: number;
  completion_tokens: number;
  estimated_cost_usd: number;
}

export interface Scorecard {
  delta_precision: number;
  delta_recall: number;
  delta_f1: number;
  groundedness_score: number;
  hallucination_rate: number;
  citation_accuracy: number;
  retrieval_recall_at_k: number;
  ocr_accuracy: number;
  avg_response_latency_ms: number;
  total_cost_usd: number;
}
