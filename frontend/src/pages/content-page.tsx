import { useQuery } from "@tanstack/react-query";

import { fetchData } from "../utils/api.ts";
import { Section } from "../section.tsx";
import { useEffect, useRef } from "react";

interface SectionType {
  key: string;
  title: string;
  content: string[][];
}

interface PageDataType {
  sections: SectionType[];
}

export const ContentPage: React.FC<{ id: string; type: string }> = ({
  id,
  type,
}) => {
  console.log("ContentPage", type, id);
  const currentSectionRef = useRef<HTMLDivElement | null>(null);

  const { data, error, isLoading } = useQuery<PageDataType>({
    queryKey: ["ContentPage", id],
    queryFn: () => fetchData(type === "toc" ? "page" : type, { key: id }),
  });

  useEffect(() => {
    if (data && data.sections.length > 0 && type === "section") {
      currentSectionRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [type, data, id]);

  if (isLoading) {
    return <div>טוען...</div>;
  }

  if (error) {
    return <div>שגיאה: {error.message}</div>;
  }

  console.log(data);
  return (
    <>
      {data &&
        data.sections.map((it) => (
          <div key={it.key} ref={it.key == id ? currentSectionRef : undefined}>
            <Section content={it.content} highlight={""} />
          </div>
        ))}
    </>
  );
};
