import { useQuery } from "@tanstack/react-query";

import { fetchData } from "./api.ts";

export const Search: React.FC<{ searchKey: string }> = ({ searchKey }) => {
  console.log("search", searchKey);
  const { data, error, isLoading } = useQuery({
    queryKey: ["search", searchKey],
    queryFn: () => fetchData("search", { key: searchKey ? searchKey : " " }),
  });

  if (isLoading) {
    return <div>טוען...</div>;
  }

  if (error) {
    return <div>שגיאה: {error.message}</div>;
  }

  return <pre>{JSON.stringify(data)}</pre>;
};
