import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  Upload, 
  LayoutDashboard, 
  CreditCard, 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  Loader2,
  CheckCircle2,
  AlertCircle,
  Search,
  Filter
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

// API Config
const API_BASE = 'http://localhost:8000/api/v1/transactions';

interface Transaction {
  id: string;
  date: string;
  amount: number;
  description: string;
  category_id?: string;
  account_id: string;
}

interface Account {
  id: string;
  name: string;
  institution: string;
}

const App: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error', msg: string } | null>(null);

  const fetchAccounts = async () => {
    try {
      const res = await axios.get(`${API_BASE}/accounts`);
      setAccounts(res.data);
      if (res.data.length > 0 && !selectedAccountId) {
        setSelectedAccountId(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch accounts', err);
    }
  };

  const fetchTransactions = useCallback(async () => {
    if (!selectedAccountId) return;
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/?account_id=${selectedAccountId}`);
      setTransactions(res.data);
    } catch (err) {
      console.error('Failed to fetch transactions', err);
    } finally {
      setLoading(false);
    }
  }, [selectedAccountId]);

  useEffect(() => {
    fetchAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccountId) {
      fetchTransactions();
    }
  }, [selectedAccountId, fetchTransactions]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0] || !selectedAccountId) return;
    
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('account_id', selectedAccountId);

    setUploading(true);
    setUploadStatus(null);
    try {
      await axios.post(`${API_BASE}/upload`, formData);
      setUploadStatus({ type: 'success', msg: 'File uploaded and processing started!' });
      // Refresh transactions after a delay to allow worker to process
      setTimeout(fetchTransactions, 2000);
    } catch (err) {
      setUploadStatus({ type: 'error', msg: 'Failed to upload file. Check if API is running.' });
    } finally {
      setUploading(false);
    }
  };

  const totalBalance = transactions.reduce((acc, t) => acc + t.amount, 0);
  const income = transactions.filter(t => t.amount > 0).reduce((acc, t) => acc + t.amount, 0);
  const expense = transactions.filter(t => t.amount < 0).reduce((acc, t) => acc + t.amount, 0);

  // Chart data prep
  const chartData = transactions
    .slice()
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map(t => ({
      date: t.date,
      amount: t.amount
    }));

  return (
    <div className="container">
      {/* Header */}
      <header className="flex-between" style={{ marginBottom: '2.5rem' }}>
        <div>
          <h1 style={{ fontSize: '2.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <LayoutDashboard size={32} strokeWidth={2.5} />
            RupeePlan
          </h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>Financial Operations Dashboard</p>
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <select 
            value={selectedAccountId} 
            onChange={(e) => setSelectedAccountId(e.target.value)}
            style={{ 
              padding: '0.625rem', 
              borderRadius: 'var(--radius)', 
              border: '1px solid var(--border-color)',
              background: 'white',
              fontWeight: 600,
              color: 'var(--primary-blue)'
            }}
          >
            <option value="">Select Account</option>
            {accounts.map(acc => (
              <option key={acc.id} value={acc.id}>{acc.name} ({acc.institution})</option>
            ))}
          </select>

          <label className="btn btn-primary">
            <Upload size={18} />
            {uploading ? 'Processing...' : 'Import CSV'}
            <input type="file" hidden accept=".csv" onChange={handleFileUpload} disabled={uploading || !selectedAccountId} />
          </label>
        </div>
      </header>

      {/* Upload Status Toast */}
      <AnimatePresence>
        {uploadStatus && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            style={{
              padding: '1rem',
              borderRadius: 'var(--radius)',
              background: uploadStatus.type === 'success' ? '#ecfdf5' : '#fef2f2',
              color: uploadStatus.type === 'success' ? 'var(--success)' : 'var(--error)',
              border: `1px solid ${uploadStatus.type === 'success' ? 'var(--success)' : 'var(--error)'}`,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            {uploadStatus.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
            {uploadStatus.msg}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats Overview */}
      <div className="dashboard-grid">
        <motion.div className="card" whileHover={{ y: -4 }}>
          <div className="flex-between" style={{ marginBottom: '1rem' }}>
            <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>Net Balance</span>
            <div style={{ background: '#e0f2fe', padding: '0.5rem', borderRadius: '50%', color: 'var(--primary-blue)' }}>
              <CreditCard size={20} />
            </div>
          </div>
          <h2 style={{ fontSize: '2rem' }}>₹{totalBalance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h2>
          <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
            <span className="text-success" style={{ fontWeight: 600 }}>↑ 12%</span> vs last month
          </div>
        </motion.div>

        <motion.div className="card" whileHover={{ y: -4 }}>
          <div className="flex-between" style={{ marginBottom: '1rem' }}>
            <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>Monthly Income</span>
            <div style={{ background: '#dcfce7', padding: '0.5rem', borderRadius: '50%', color: 'var(--success)' }}>
              <TrendingUp size={20} />
            </div>
          </div>
          <h2 style={{ fontSize: '2rem' }}>₹{income.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Across all deposits</p>
        </motion.div>

        <motion.div className="card" whileHover={{ y: -4 }}>
          <div className="flex-between" style={{ marginBottom: '1rem' }}>
            <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>Monthly Spending</span>
            <div style={{ background: '#fee2e2', padding: '0.5rem', borderRadius: '50%', color: 'var(--error)' }}>
              <TrendingDown size={20} />
            </div>
          </div>
          <h2 style={{ fontSize: '2rem' }}>₹{Math.abs(expense).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Across all expenses</p>
        </motion.div>
      </div>

      {/* Charts Section */}
      <div className="card" style={{ marginBottom: '1.5rem', height: '400px' }}>
        <div className="flex-between" style={{ marginBottom: '1rem' }}>
          <div>
            <h3>Cash Flow Trend</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Daily transaction volume</p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', fontWeight: 600 }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary-blue)' }}></div>
              Inflow
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', fontWeight: 600 }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary-red)' }}></div>
              Outflow
            </span>
          </div>
        </div>
        
        <ResponsiveContainer width="100%" height="85%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--primary-blue)" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="var(--primary-blue)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
            <XAxis 
              dataKey="date" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              minTickGap={30}
              tickFormatter={(str) => new Date(str).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              tickFormatter={(val) => `₹${val}`}
            />
            <Tooltip 
              contentStyle={{ 
                borderRadius: 'var(--radius)', 
                border: 'none', 
                boxShadow: 'var(--shadow-md)',
                fontSize: '0.875rem'
              }} 
            />
            <Area 
              type="monotone" 
              dataKey="amount" 
              stroke="var(--primary-blue)" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorAmount)" 
              animationBegin={0}
              animationDuration={1500}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Main Content Area */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
        {/* Transactions Table */}
        <div className="card">
          <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
            <h3>Recent Transactions</h3>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <div style={{ position: 'relative' }}>
                <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input 
                  type="text" 
                  placeholder="Search..." 
                  style={{ 
                    padding: '0.5rem 0.5rem 0.5rem 2rem', 
                    borderRadius: 'var(--radius)', 
                    border: '1px solid var(--border-color)',
                    fontSize: '0.875rem'
                  }} 
                />
              </div>
              <button className="btn btn-outline" style={{ padding: '0.5rem 0.75rem', fontSize: '0.875rem' }}>
                <Filter size={16} />
                Filter
              </button>
            </div>
          </div>

          <div className="table-container">
            {loading ? (
              <div style={{ padding: '4rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                <Loader2 className="animate-spin" size={32} color="var(--primary-blue)" />
                <p>Loading transactions...</p>
              </div>
            ) : transactions.length === 0 ? (
              <div style={{ padding: '4rem', textAlign: 'center' }}>
                <AlertCircle size={48} style={{ color: 'var(--text-muted)', marginBottom: '1rem' }} />
                <p>No transactions found. Upload a bank statement to get started.</p>
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th style={{ textAlign: 'right' }}>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((t) => (
                    <motion.tr 
                      key={t.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      <td style={{ fontWeight: 500 }}>{new Date(t.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</td>
                      <td>{t.description}</td>
                      <td>
                        <span style={{ 
                          padding: '0.25rem 0.75rem', 
                          borderRadius: '12px', 
                          fontSize: '0.75rem', 
                          background: '#f1f5f9',
                          fontWeight: 600,
                          color: 'var(--text-muted)'
                        }}>
                          Uncategorized
                        </span>
                      </td>
                      <td style={{ 
                        textAlign: 'right', 
                        fontWeight: 700,
                        color: t.amount > 0 ? 'var(--success)' : 'var(--text-main)'
                      }}>
                        {t.amount > 0 ? '+' : ''}₹{t.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
