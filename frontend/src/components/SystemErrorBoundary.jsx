import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import logger from '../lib/logger';

export default class SystemErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, info: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, info) {
    this.setState({ info });
    if (window.logClientError) {
      window.logClientError({ message: error?.message, stack: error?.stack, info });
    }
    // Optional: console for dev
    // eslint-disable-next-line no-console
    logger.error('UI ErrorBoundary caught:', error, info);
  }
  onReload = () => window.location.reload();
  onCopy = () => {
    const text = `${this.state.error?.message || ''}\n\n${this.state.error?.stack || ''}`;
    navigator.clipboard.writeText(text).catch(() => {});
  };
  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div className="container mx-auto px-4 py-12 max-w-3xl">
        <Card>
          <CardHeader>
            <CardTitle>Something went wrong</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">An unexpected error occurred. You can try reloading the page. If the problem persists, please contact support.</p>
            <div className="mt-4 flex items-center gap-2">
              <Button onClick={this.onReload}>Reload</Button>
              <Button variant="outline" onClick={this.onCopy}>Copy details</Button>
            </div>
            {this.state.error?.message && (
              <pre className="mt-4 p-3 bg-muted rounded text-xs overflow-auto max-h-64">{this.state.error.message}</pre>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }
}