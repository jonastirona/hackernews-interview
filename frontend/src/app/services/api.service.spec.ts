import { TestBed } from '@angular/core/testing';
import { ApiService } from './api.service';

class MockEventSource {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSED = 2;

  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  close = jest.fn();

  constructor(public url: string) {}
}

describe('ApiService', () => {
  let service: ApiService;
  let mockEventSource: MockEventSource;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ApiService]
    });
    service = TestBed.inject(ApiService);
    mockEventSource = new MockEventSource('');
    global.EventSource = jest.fn().mockImplementation(() => mockEventSource) as unknown as typeof EventSource;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should create EventSource with correct URL', () => {
    service.getArticles(5).subscribe();
    expect(EventSource).toHaveBeenCalledWith('/analyze?offset=5&limit=10');
  });

  it('should handle messages correctly', (done) => {
    const testData = { title: 'Test Article' };
    const mockEvent = { data: JSON.stringify(testData) } as MessageEvent;

    service.getArticles().subscribe(data => {
      expect(data).toEqual(testData);
      done();
    });

    if (mockEventSource.onmessage) {
      mockEventSource.onmessage(mockEvent);
    }
  });

  it('should handle errors correctly', (done) => {
    const testError = new Event('error');

    service.getArticles().subscribe({
      error: (error) => {
        expect(error).toStrictEqual(testError);
        setTimeout(() => {
          expect(mockEventSource.close).toHaveBeenCalled();
          done();
        }, 0);
      }
    });

    if (mockEventSource.onerror) {
      mockEventSource.onerror(testError);
    }
  });
}); 