import { Component, type ErrorInfo, type ReactNode } from 'react'
import { ErrorMessage } from './ui/ErrorMessage'

interface State {
  error: Error | null
}

/** Global catch-all for render errors so the app never shows a blank page. */
export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unhandled UI error', error, info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="mx-auto max-w-xl p-8">
          <ErrorMessage message="Something went wrong. Please reload the page." />
        </div>
      )
    }
    return this.props.children
  }
}
