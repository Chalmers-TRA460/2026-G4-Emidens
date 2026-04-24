interface PlaceholderPageProps {
  title: string;
}

export function PlaceholderPage({ title }: PlaceholderPageProps) {
  return (
    <div className="flex-1 flex items-center justify-center bg-[#f7f8fa]">
      <div className="text-center">
        <h1 className="text-xl font-semibold text-gray-900 mb-2">{title}</h1>
        <p className="text-sm text-gray-500">This page is under construction.</p>
      </div>
    </div>
  );
}
