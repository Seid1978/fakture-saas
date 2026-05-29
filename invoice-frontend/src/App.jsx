import { useState, useEffect } from "react";
import Login from "./Login";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [active, setActive] = useState("dashboard");

  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    client: "",
    amount: "",
    status: "pending",
  });

  // --------------------
  // AUTH HANDLERS
  // --------------------
  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  // --------------------
  // FETCH INVOICES
  // --------------------
  useEffect(() => {
    if (token && active === "invoices") {
      fetchInvoices();
    }
  }, [active, token]);

  const fetchInvoices = async () => {
    try {
      setLoading(true);

      const res = await fetch("http://localhost:8000/invoices", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      setInvoices(data);
    } catch (err) {
      console.log("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  // --------------------
  // FORM HANDLER
  // --------------------
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  // --------------------
  // CREATE INVOICE
  // --------------------
  const createInvoice = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch("http://localhost:8000/invoices", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        throw new Error("Create failed");
      }

      setForm({
        client: "",
        amount: "",
        status: "pending",
      });

      fetchInvoices();
      setActive("invoices");
    } catch (err) {
      console.log(err);
    }
  };

  // --------------------
  // DELETE INVOICE
  // --------------------
  const deleteInvoice = async (id) => {
    try {
      const res = await fetch(
        `http://localhost:8000/invoices/${id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        throw new Error("Delete failed");
      }

      fetchInvoices();
    } catch (err) {
      console.log(err);
    }
  };

  // --------------------
  // LOGIN GATE
  // --------------------
  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "Arial" }}>
      
      {/* SIDEBAR */}
      <div
        style={{
          width: "220px",
          background: "#111827",
          color: "white",
          padding: "20px",
        }}
      >
        <h2 style={{ marginBottom: "30px" }}>Invoice SaaS</h2>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          <button onClick={() => setActive("dashboard")}>
            Dashboard
          </button>

          <button onClick={() => setActive("invoices")}>
            Invoices
          </button>

          <button onClick={() => setActive("create")}>
            Create Invoice
          </button>

          <button onClick={logout} style={{ marginTop: "20px" }}>
            Logout
          </button>
        </div>
      </div>

      {/* MAIN */}
      <div style={{ flex: 1, background: "#f3f4f6" }}>
        
        {/* TOPBAR */}
        <div
          style={{
            height: "60px",
            background: "white",
            display: "flex",
            alignItems: "center",
            padding: "0 20px",
            borderBottom: "1px solid #e5e7eb",
          }}
        >
          <h3 style={{ margin: 0, textTransform: "capitalize" }}>
            {active}
          </h3>
        </div>

        {/* CONTENT */}
        <div style={{ padding: "20px" }}>
          
          {/* DASHBOARD */}
          {active === "dashboard" && (
            <div>
              <h2>Dashboard</h2>
              <p>Welcome to your SaaS app 🚀</p>
            </div>
          )}

          {/* INVOICES */}
          {active === "invoices" && (
            <div>
              <h2>Invoices</h2>

              {loading ? (
                <p>Loading...</p>
              ) : (
                <table
                  style={{
                    width: "100%",
                    background: "white",
                    borderCollapse: "collapse",
                    marginTop: "20px",
                  }}
                >
                  <thead>
                    <tr>
                      <th style={th}>ID</th>
                      <th style={th}>Client</th>
                      <th style={th}>Amount</th>
                      <th style={th}>Status</th>
                      <th style={th}>Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    {invoices.length === 0 ? (
                      <tr>
                        <td style={td} colSpan="5">
                          No invoices found
                        </td>
                      </tr>
                    ) : (
                      invoices.map((inv) => (
                        <tr key={inv.id}>
                          <td style={td}>{inv.id}</td>
                          <td style={td}>{inv.client}</td>
                          <td style={td}>{inv.amount} €</td>
                          <td style={td}>{inv.status}</td>
                          <td style={td}>
                            <button
                              onClick={() => deleteInvoice(inv.id)}
                              style={{
                                background: "red",
                                color: "white",
                                border: "none",
                                padding: "5px 10px",
                                cursor: "pointer",
                              }}
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {/* CREATE */}
          {active === "create" && (
            <div>
              <h2>Create Invoice</h2>

              <form
                onSubmit={createInvoice}
                style={{
                  background: "white",
                  padding: "20px",
                  marginTop: "20px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                  maxWidth: "400px",
                }}
              >
                <input
                  name="client"
                  placeholder="Client"
                  value={form.client}
                  onChange={handleChange}
                />

                <input
                  name="amount"
                  type="number"
                  placeholder="Amount"
                  value={form.amount}
                  onChange={handleChange}
                />

                <select
                  name="status"
                  value={form.status}
                  onChange={handleChange}
                >
                  <option value="pending">Pending</option>
                  <option value="paid">Paid</option>
                </select>

                <button type="submit">Create</button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const th = {
  textAlign: "left",
  padding: "10px",
  borderBottom: "1px solid #e5e7eb",
};

const td = {
  padding: "10px",
  borderBottom: "1px solid #e5e7eb",
};

export default App;