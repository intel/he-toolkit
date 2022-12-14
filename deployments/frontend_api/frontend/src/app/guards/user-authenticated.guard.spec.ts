import { TestBed } from '@angular/core/testing';

import { UserAuthenticatedGuard } from './user-authenticated.guard';

describe('UserAuthenticatedGuard', () => {
  let guard: UserAuthenticatedGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(UserAuthenticatedGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
