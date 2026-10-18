/* grubpatch - switch mungwall on or off in the AROS Portable Games (aros.games)
 * boot menu. Its GRUB menu has a timeout of 0, so the option cannot be added
 * at boot time.
 *
 *   grubpatch          adds "mungwall" to the default entry, after saving the
 *                      original as SYS:boot/grub/grub.cfg.orig
 *   grubpatch RESTORE  puts grub.cfg.orig back and deletes it
 *
 * Only the exact aros.games v1.0 line is changed; anything else is refused.
 * Takes effect at the next boot. */
#include <stdio.h>
#include <string.h>

#define CFG "SYS:boot/grub/grub.cfg"
#define ORIG "SYS:boot/grub/grub.cfg.orig"

static const char *old = "ATA=32bit $bootstrap_flags";
static const char *new = "ATA=32bit mungwall $bootstrap_flags";
static char buf[65536];

static long load(const char *path)
{
    FILE *f = fopen(path, "rb");
    size_t n;
    if (!f)
        return -1;
    n = fread(buf, 1, sizeof buf - 1, f);
    if (!feof(f)) {
        fclose(f);
        return -2;
    }
    fclose(f);
    buf[n] = 0;
    return (long)n;
}

static int save(const char *path, const char *a, size_t na, const char *b, const char *c)
{
    FILE *f = fopen(path, "wb");
    if (!f)
        return 0;
    fwrite(a, 1, na, f);
    if (b)
        fputs(b, f);
    if (c)
        fputs(c, f);
    return fclose(f) == 0;
}

static int restore(void)
{
    long n = load(ORIG);
    if (n < 0) {
        puts("grubpatch: no " ORIG " - nothing to restore");
        return 10;
    }
    if (!save(CFG, buf, (size_t)n, NULL, NULL)) {
        puts("grubpatch: cannot write " CFG " - " ORIG " kept");
        return 20;
    }
    remove(ORIG);
    puts("grubpatch: original boot menu restored; reboot to switch mungwall off");
    return 0;
}

int main(int argc, char **argv)
{
    long n;
    char *at;
    FILE *o;

    if (argc > 1 && strcmp(argv[1], "RESTORE") == 0)
        return restore();
    if (argc > 1) {
        puts("usage: grubpatch [RESTORE]");
        return 10;
    }
    n = load(CFG);
    if (n < 0) {
        puts("grubpatch: cannot read " CFG);
        return 20;
    }
    if (strstr(buf, "mungwall")) {
        puts("grubpatch: mungwall is already in " CFG);
        return 5;
    }
    at = strstr(buf, old);
    if (!at) {
        puts("grubpatch: this is not the aros.games v1.0 boot menu - nothing changed");
        return 20;
    }
    if ((o = fopen(ORIG, "rb"))) {
        fclose(o);
        puts("grubpatch: " ORIG " already exists - nothing changed");
        return 20;
    }
    if (!save(ORIG, buf, (size_t)n, NULL, NULL)) {
        puts("grubpatch: cannot save " ORIG " - nothing changed");
        return 20;
    }
    if (!save(CFG, buf, (size_t)(at - buf), new, at + strlen(old))) {
        puts("grubpatch: writing " CFG " failed - run: grubpatch RESTORE");
        return 20;
    }
    puts("grubpatch: mungwall added; reboot to switch it on");
    return 0;
}
