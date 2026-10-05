import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import App from './App';

test('renders intersection and union as accessible math in an answer', async () => {
  const originalFetch = global.fetch;
  const fetchMock = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ reply: 'Intersection: $A \\cap B$. Union: $A \\cup B$.\n\n$$\nA \\cap B = \\emptyset\n$$\n\nSOURCE: lecture.pdf (page 8)' }),
  } as Response);
  global.fetch = fetchMock;
  try {
    const { container } = render(<App />);
    fireEvent.change(screen.getByRole('textbox', { name: 'Course question' }), {
      target: { value: 'Explain intersection and union' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    await screen.findByText(/Intersection:/);
    expect(container.querySelectorAll('.katex')).toHaveLength(3);
    expect(container.querySelector('.katex-display')).toBeInTheDocument();
    expect(container.querySelector('math')).not.toBeNull();
    expect(container.querySelector('.katex-mathml')?.textContent).toContain('∩');
    expect(container.querySelectorAll('.katex-mathml')[1].textContent).toContain('∪');
    expect(container.querySelector('.katex-error')).toBeNull();
    expect(screen.getByText('lecture.pdf (page 8)')).toBeInTheDocument();
    expect(container.querySelector('.response')?.textContent).not.toContain('SOURCE:');
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/chat', expect.objectContaining({
      body: JSON.stringify({ message: 'Explain intersection and union' }),
    }));
  } finally {
    global.fetch = originalFetch;
  }
});

 test('topic suggestions prepare a question without submitting it', () => {
  render(<App />);
  expect(screen.getByRole('button', { name: 'Ask' })).toBeDisabled();
  fireEvent.click(screen.getByRole('button', { name: 'Assignment 1' }));
  expect(screen.getByRole('textbox', { name: 'Course question' })).toHaveValue('According to Assignment 1, what makes a valid identifier?');
  expect(screen.getByRole('button', { name: 'Ask' })).toBeEnabled();
});
