import { useQuery } from "@tanstack/react-query";

import { fetchData } from "./api.ts";

interface SectionType {
  key: string;
  title: string;
  content: string;
}

interface PageDataType {
  sections: SectionType[];
}

const Section: React.FC<{ title: string; content: string }> = ({
  title,
  content,
}) => {
  return (
    <p>
      כותרת: {title}
      <br />
      תוכן: {content}
    </p>
  );
};

export const Page: React.FC<{ pageKey: string }> = ({ pageKey }) => {
  console.log("page", pageKey);
  const { data, error, isLoading } = useQuery<PageDataType>({
    queryKey: ["Page", pageKey],
    queryFn: () => fetchData("page", { key: pageKey }),
  });

  if (isLoading) {
    return <div>טוען...</div>;
  }

  if (error) {
    return <div>שגיאה: {error.message}</div>;
  }

  return (
    <>
      {data &&
        data.sections.map((it) => (
          <Section key={it.key} title={it.title} content={it.content} />
        ))}
    </>
  );
};
