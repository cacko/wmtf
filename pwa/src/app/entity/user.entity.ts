
export enum Gender {
  MALE = 'male',
  FEMALE = 'female',
  UNKNOWN = 'unknown',
}

export enum AvatarGender {
  MALE = '03',
  FEMALE = '01',
  UNKNOWN = '00,02,04,05,06,07,08,09,10,11,12,13,14,15',
}

export interface AppUserEntity {
  uid: string;
  displayName: string | null;
  email: string | null;
  photoURL: string | null;
}

export interface User  {
  isAdmin?: boolean;
}
