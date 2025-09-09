# Frontend integration (React + Axios)

This guide shows how to consume Students APIs from a React app.

## Axios instance
```javascript
import axios from 'axios';

export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000' });

export function setAuthToken(token) {
  api.defaults.headers.common.Authorization = `Bearer ${token}`;
}
```

## Types (TypeScript)
```ts
export type Student = {
  id: string;
  roll_number: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: 'M' | 'F' | 'O';
  email?: string | null;
  section?: 'A' | 'B' | 'C' | 'D' | 'E' | null;
};
```

## API functions
```ts
export async function listStudents(params?: Record<string, any>) {
  const { data } = await api.get('/api/v1/students/students/', { params });
  return data;
}

export async function createStudent(payload: Partial<Student>) {
  const { data } = await api.post('/api/v1/students/students/', payload);
  return data;
}

export async function updateStudent(id: string, patch: Partial<Student>) {
  const { data } = await api.patch(`/api/v1/students/students/${id}/`, patch);
  return data;
}
```

## Form example
```tsx
import { useState } from 'react';
import { createStudent } from './api';

export function CreateStudentForm() {
  const [form, setForm] = useState({ roll_number: '', first_name: '', last_name: '', date_of_birth: '', gender: 'M' });
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await createStudent(form);
      alert('Student created');
    } catch (err: any) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Failed');
    }
  }

  return (
    <form onSubmit={onSubmit}>
      {/* inputs for roll_number, first_name, last_name, date_of_birth, gender */}
      <button type="submit">Create</button>
      {error && <pre>{error}</pre>}
    </form>
  );
}
```

## Handling file upload (documents)
```ts
export async function uploadStudentDocument(studentId: string, file: File, docType = 'PHOTO_ID') {
  const form = new FormData();
  form.append('student', studentId);
  form.append('file', file);
  form.append('doc_type', docType);
  const { data } = await api.post('/api/v1/students/documents/', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  return data;
}
```

## Search and stats
```ts
export const searchStudents = (q: string) => api.get('/api/v1/students/students/search/', { params: { q } }).then(r => r.data);
export const studentStats = () => api.get('/api/v1/students/students/stats/').then(r => r.data);
```

Notes:
- Debounce search inputs (≈300ms).
- Handle 401 by redirecting to login and clearing token.
- Validate `roll_number`/`email` uniqueness errors from API and surface inline.

