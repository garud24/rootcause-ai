type Props = {
  value: string;
  onChange: (value: string) => void;
};

export default function ErrorInput({
  value,
  onChange,
}: Props) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium">
        Error or Stack Trace
      </label>

      <textarea
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
        placeholder="Error: connect ECONNREFUSED 127.0.0.1:5432"
        rows={8}
        className="w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 font-mono outline-none focus:border-gray-500"
      />
    </div>
  );
}