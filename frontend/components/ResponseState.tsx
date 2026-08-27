"use client";

import { ChatResponse } from "@/lib/api";
import { AnswerCard } from "./AnswerCard";
import { GapCard } from "./GapCard";
import { RefusalCard } from "./RefusalCard";
import { ChoiceCard } from "./ChoiceCard";
import { NoticeCard } from "./NoticeCard";
import { EmptyState } from "./EmptyState";

interface ResponseStateProps {
  response: ChatResponse | null;
  onPick: (query: string) => void;
  onPickScheme: (schemeId: string) => void;
  onRetry?: () => void;
}

export function ResponseState({
  response,
  onPick,
  onPickScheme,
  onRetry,
}: ResponseStateProps) {
  if (!response) {
    return <EmptyState onPick={onPick} />;
  }

  switch (response.state) {
    case "answer":
      return <AnswerCard response={response} onPick={onPick} />;

    case "known_gap":
    case "no_evidence":
      return <GapCard response={response} onPick={onPick} />;

    case "refusal":
      return <RefusalCard response={response} onPick={onPick} />;

    case "needs_scheme":
      return (
        <ChoiceCard
          response={response}
          onPickScheme={onPickScheme}
        />
      );

    case "pii":
      return <NoticeCard type="pii" message={response.message} />;

    case "too_long":
      return <NoticeCard type="too_long" message={response.message} />;

    case "error":
    default:
      return (
        <NoticeCard
          type="error"
          message={response.message}
          onRetry={onRetry}
        />
      );
  }
}
