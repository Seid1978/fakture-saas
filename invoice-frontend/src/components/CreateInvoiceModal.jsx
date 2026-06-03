import { useState } from "react";
import { createInvoice } from "../services/invoices";

export default function CreateInvoiceModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    client: "",
    amount: "",
    status: "Pending",
    date: "",
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      await createInvoice({
        ...form,
        amount: Number(form.amount),
      });

      onCreated(); // refresh dashboard
      onClose();   // zatvori modal
    } catch (err) {
      console.error("Create invoice error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">

      <div className="bg-white w-full max-w-md rounded-xl p-6 shadow-lg">

        <h2 className="text-xl font-semibold mb-4">
          Nova faktura
        </h2>

        <form onSubmit={handleSubmit} className="space-y-3">

          <input
            name="client"
            placeholder="Klijent"
            className="w-full border p-2 rounded"
            onChange={handleChange}
            required
          />

          <input
            name="amount"
            type="number"
            placeholder="Iznos"
            className="w-full border p-2 rounded"
            onChange={handleChange}
            required
          />

          <select
            name="status"
            className="w-full border p-2 rounded"
            onChange={handleChange}
          >
            <option value="Pending">Pending</option>
            <option value="Paid">Paid</option>
          </select>

          <input
            name="date"
            type="date"
            className="w-full border p-2 rounded"
            onChange={handleChange}
          />

          <div className="flex justify-end gap-2 pt-3">

            <button
              type="button"
              onClick={onClose}
              className="px-3 py-2 border rounded"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
              className="px-3 py-2 bg-black text-white rounded"
            >
              {loading ? "Saving..." : "Save"}
            </button>

          </div>

        </form>

      </div>
    </div>
  );
}